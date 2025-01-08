import os
import datetime
import argparse
import statistics

# ----- INPUT CONSTANT -----
# set by command line argument, show default below
RESULT_ROOT_FOLDER = "test_results"
REPORT_FILE = "analysis.csv"
EXTRA_IDENTIFIERS = None
EXTRA_COUNTS = None
EXTRA_TIME = None
EXTRA_DETAILS = None

# ----- CONSTANT -----
# not changed
EXCLUDE_FOLDERS = {"current", "latest"}
LOG_FILE = "jepsen.log"
LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
OUTPUT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CAN_INFER_NEMESIS_TIME = {"kill", "partition", "pause", "stop", "member"}
T_IDENTIFIER = "Workload,Nemesis,TimeLimit,TestCount,Concurrency,NemesisInterval,Folder" # this is the basic identifier for each test
T_COUNTS = "Invoke,Valid,Failed,NemesisStart,NemesisStop" # this is the basic counts need to provide
T_TIME =  "Runtime,NemStartTime,NemStopTime,RecoverToFirstOk,RecoverToFirstWrite,RecoverToAllGood" # this is the basic time measurements needed to provide
T_DETAILS = "VerifyResult,Failures,Notes" # this is the basic details need to provide

# TODO: consider setup parsing profile for each nemesis in json

# ----- Functions -----

def cmd_parser():
    global RESULT_ROOT_FOLDER
    global REPORT_FILE
    global EXTRA_IDENTIFIERS
    # Create the parser
    parser = argparse.ArgumentParser(description="Parsor for parser command line arguement")
    
    # Add arguments
    parser.add_argument('-p', '--path', type=str, required=True, help="Folder path for test results")
    parser.add_argument('-o', '--output', type=str, required=False, help="Output csv file name, default is 'analysis.csv'", default='analysis.csv')
    parser.add_argument('--extra-id', type=str, required=False, help="Comma seperated list of extra ids", default=None)
    # parser.add_argument('-v', '--verbose', action='store_true', help="Increase output verbosity")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Set arguments
    RESULT_ROOT_FOLDER = args.path
    REPORT_FILE = args.output
    EXTRA_IDENTIFIERS = args.extra_id # [x.strip() for x in args.extra_id.split(',') if x.strip()] if args.extra_id else None
    # print("Extra ids", EXTRA_IDENTIFIERS)


def get_folder_list(root_folder, folder_filter=lambda x: x not in EXCLUDE_FOLDERS):
    folder_list = os.listdir(root_folder)
    folder_list = filter(folder_filter, folder_list)
    return folder_list


def set_csv_header(extra_ids=None, extra_counts=None, extra_time=None, extra_details=None):
    identifier = f"{T_IDENTIFIER},{extra_ids}" if extra_ids else T_IDENTIFIER
    counts = f"{T_COUNTS},{extra_counts}" if extra_counts else T_COUNTS
    times = f"{T_TIME},{extra_time}" if extra_time else T_TIME
    details = f"{T_DETAILS},{extra_details}" if extra_details else T_DETAILS

    # Set up headers
    header = f"{identifier},{counts},{times},{details}\n"
    with open(REPORT_FILE, "w") as f:
        f.write(header)


def parse_time(line):
    time_str = line.split('{')[0]
    return datetime.datetime.strptime(time_str, LOG_TIME_FORMAT)


def parse_test_options(line, extra_ids=None):
    args = line.split()
    opts = {
        "workload": args[args.index("--workload") + 1],
        "nemesis": args[args.index("--nemesis") + 1],
        "time-limit": args[args.index("--time-limit") + 1],
        "test-count": args[args.index("--test-count") + 1],
        "concurrency": args[args.index("--concurrency") + 1],
        "nemesis-interval": args[args.index("--nemesis-interval") + 1] if "--nemesis-interval" in args else "3",
    }
    if extra_ids:
        extra_id_list = [x.strip() for x in extra_ids.split(',') if x.strip()]
        if "Rate" in extra_id_list:
            if "--rate" in args:
                opts["rate"] = args[args.index("--rate") + 1]
            elif "-r" in args:
                opts["rate"] = args[args.index("-r") + 1]
            else:
                opts["rate"] = "1000"
        # TODO: to be implemented
    return opts


def get_nemesis_sign(nemesis):
    # nemesis -- kill
    if nemesis == "kill":
        return ([":kill"], [":start"])
    # nemesis -- partition
    elif nemesis == "partition":
        return ([":start-partition"], [":stop-partition"])
    # nemesis -- pause
    elif nemesis == "pause":
        return ([":pause"], [":resume"])
    # nemesis -- (dqlite) stop-node
    elif nemesis == "stop":
        return ([":stop-node"], [":start-node"])
    elif nemesis == "clock":
        # TODO: need to see how this thing works
        return  ([":reset-clock", ":strobe-clock", ":bump-clock", ":check-clock-offsets"], [])
    elif nemesis == "member":
        return ([":remove-members"], [":add-members"])
    # all others
    else:
        return (None, None)


def loop_until(file, condition):
    found = False
    while not found:
        line = file.readline()
        if not line:
            # Stop at EOF
            break
        if condition(line):
            found = True
    return found


def stats_on_time(list_s, list_t):
    none_cnt = list_t.count(None)
    if len(list_t) == 0 or none_cnt == len(list_t):
        return f"Nemesis has no recovery at all"
    # if none_cnt > 0:
    #     return f"{none_cnt} nemesis not recovered"

    # Must have some recovery
    pairs = [(s, t) for s, t in zip(list_s, list_t) if t is not None]
    times = [round((t - s).total_seconds(), 3) for (s, t) in pairs]
    avg = round(sum(times) / len(times), 3)
    maxt, mint, stdt = max(times), min(times), round(statistics.stdev(times), 3) if len(times) > 1 else 0
    stats = f"avg:{avg}; max:{maxt}; min:{mint}; sd:{stdt}"
    not_recovered = f"{none_cnt} nemesis not recovered" if none_cnt > 0 else ""
    return f"{stats};{not_recovered}"


def processing_test(f, nemesis, nem_start_signs, nem_stop_signs, workload):
    # print("\tTODO: processing")
    finished = False

    # For cnt
    invoke_cnt, ok_cnt, locked_cnt, not_prim_cnt, failed_cnt, nemesis_start_cnt, nemesis_stop_cnt = 0, 0, 0, 0, 0, 0, 0
    # For time
    can_calcu_time = nemesis in CAN_INFER_NEMESIS_TIME
    nemesis_start_s, nemesis_start_t = [], []
    nemesis_stop_s, nemesis_stop_t = [], []
    # recover to ok, and rocover to last fail
    found_recover_to_first_ok, found_recover_to_first_write, to_find_all_good = True, True, False
    recover_to_first_ok, recover_to_first_write, recover_to_allgood = [], [], []

    

    # For details
    failed_reasons = set()
    while True:
        line = f.readline()
        if not line:
            # stop if EOF
            break
        elif "Run complete" in line:
            # Stop with Test ends
            finished = True
            # If the last stop has not received OK, use None to indicate it is not covered
            if not found_recover_to_first_ok:
                recover_to_first_ok.append(None)
            if not found_recover_to_first_write:
                recover_to_first_write.append(None)
            break
        elif ":invoke" in line:
            # Invoking a request
            invoke_cnt += 1
        elif ":ok" in line:
            # request succeeded
            ok_cnt += 1
            # Calculate recovery time
            if not found_recover_to_first_ok:
                found_recover_to_first_ok = True
                recover_to_first_ok.append(parse_time(line))
            if not found_recover_to_first_write:
                # if nemesis == "member":
                if workload == "list-append":
                    if ":append" in line: # for member nemesis, has to find the first successful append
                        found_recover_to_first_write = True
                        recover_to_first_write.append(parse_time(line))
                else:
                    print("Not implemented")
                    pass
        elif ":fail" in line:
            # fail might be expected
            if ":locked" in line:
                locked_cnt += 1
            elif ":not-primary" in line: # For mongodb this is as expected
                not_prim_cnt += 1
            else:
                failed_cnt += 1
                failed_reasons.add(line.split()[-1])
                if to_find_all_good: # when need to find the last failure after recovery
                    recover_to_allgood[-1] = parse_time(line)
        elif ":info" in line:
            if ":nemesis" not in line:
                # normal info are generally failed operations
                # timeout failer in mongodb seems to be a valid operation, don't count for failure in recover_to_allgood
                failed_cnt += 1
                failed_reasons.add(line.split()[-1])
            elif nem_start_signs is not None:
                # For nemesis info need to parse based on specific nemesis sign
                if any(s in line for s in nem_start_signs):
                    nemesis_start_cnt += 1
                    # when start a nemesis, previous recover to all good stopps
                    to_find_all_good = False
                    # Use None to indicate that previous case not recovered
                    if not found_recover_to_first_ok:
                        recover_to_first_ok.append(None)
                    if not found_recover_to_first_write:
                        recover_to_first_write.append(None)
                    # avoid calculating recovery time during nemesis
                    found_recover_to_first_ok, found_recover_to_first_write = True, True
                    if can_calcu_time:
                        # If can calculate time, the start command should appear in pairs
                        if nemesis_start_cnt % 2 == 1: 
                            nemesis_start_s.append(parse_time(line))
                        else:
                            nemesis_start_t.append(parse_time(line))
                    else:
                        # Only know a new nemesis started
                        nemesis_start_s.append(parse_time(line))
                elif any(s in line for s in nem_stop_signs):
                    nemesis_stop_cnt += 1
                    if can_calcu_time:
                        # If can calculate time, the stop command should appear in pairs
                        if nemesis_stop_cnt % 2 == 1:
                            nemesis_stop_s.append(parse_time(line))
                            # To calcualte the stop to last failure time
                            to_find_all_good = True
                            # To calculate recovery time after nemesis
                            found_recover_to_first_ok, found_recover_to_first_write = False, False
                            recover_to_allgood.append(None)
                        else:
                            nemesis_stop_t.append(parse_time(line))
                    else:
                        # Only know a new nemesis stopped
                        nemesis_stop_s.append(parse_time(line))
                        # To calcualte the stop to last failure time
                        to_find_all_good = True
                        # To calculate recovery time after nemesis
                        found_recover_to_first_ok, found_recover_to_first_write = False, False

    # print(f"\t{nemesis}, {finished}, {nem_start_signs}, {nem_stop_signs}, {recover_to_first_ok}")
    if not finished:
        return None
    else:
        # Calculate counts
        success_cnt = ok_cnt + locked_cnt + not_prim_cnt
        if invoke_cnt != success_cnt + failed_cnt:
            print(f"\tWARNING: there is a count mismatch in request -- missing {invoke_cnt - success_cnt - failed_cnt} response(s)")
        if can_calcu_time:
            nemesis_start_cnt, nemesis_stop_cnt = nemesis_start_cnt // 2, nemesis_stop_cnt // 2
        # print(f"\t{success_cnt}, {failed_cnt}")

        # Calculate times
        # For nemesis start and stop
        # print(f"\tstart:{len(nemesis_start_s)}, recover:{len(nemesis_stop_s)}, first_ok:{len(recover_to_first_ok)}")
        if can_calcu_time:
            # calculate stats for nemesis start and nemesis recovery
            nem_start_time_info = stats_on_time(nemesis_start_s, nemesis_start_t)
            nem_stop_time_info = stats_on_time(nemesis_stop_s, nemesis_stop_t)
        else:
            nem_start_time_info = "NA"
            nem_stop_time_info = "NA"
        # for recover to first ok and first write
        # Not necessarily all nemesis get a recover in the timelimit, discard the very last one in calculation
        nem_recover_ok_info = stats_on_time(nemesis_stop_s, recover_to_first_ok)
        nem_recover_write_info = stats_on_time(nemesis_stop_s, recover_to_first_write)
        # for recover to last failure
        nem_recover_allgood_info = stats_on_time(nemesis_stop_s, recover_to_allgood)


        return {
            "invoke": invoke_cnt,
            "valid": success_cnt,
            "failed": failed_cnt,
            "nemesis_start": nemesis_start_cnt,
            "nemesis_stop": nemesis_stop_cnt,
            "failed_reasons": failed_reasons,
            "nem_start_time": nem_start_time_info,
            "nem_stop_time": nem_stop_time_info,
            "recover_to_first_ok": nem_recover_ok_info,
            "recover_to_first_write": nem_recover_write_info,
            "recover_to_allgood": nem_recover_allgood_info
        }


def append_to_csv(test_name, args, results):
    test_info = []
    # For identifier - Workload,Nemesis,TimeLimit,TestCount,Concurrency,NemesisInterval,Folder
    test_info.append(args["workload"])
    test_info.append(args["nemesis"])
    test_info.append(args["time-limit"])
    test_info.append(args["test-count"])
    test_info.append(args["concurrency"])
    test_info.append(args["nemesis-interval"])
    test_info.append(test_name)

    # For extra identifiers
    if "rate" in args:
        test_info.append(args["rate"])

    if "error" not in results:
        # For counts = Invoke,Valid,Failed,NemesisStart,NemesisStop 
        test_info.append(str(results["invoke"]))
        test_info.append(str(results["valid"]))
        test_info.append(str(results["failed"]))
        test_info.append(str(results["nemesis_start"]))
        test_info.append(str(results["nemesis_stop"]))
        # For times - Runtime,NemStartTime,NemStopTime,RecoverToFirstOk,RecoverToFirstWrite,RecoverToAllGood
        test_info.append(results["runtime"])
        test_info.append(results["nem_start_time"])
        test_info.append(results["nem_stop_time"])
        test_info.append(results["recover_to_first_ok"])
        test_info.append(results["recover_to_first_write"])
        test_info.append(results["recover_to_allgood"])
        # For details - VerifyResult,Failures,Notes
        test_info.append(results["verify_result"])
        test_info.append(";".join(results["failed_reasons"]))
        if results["invoke"] != results["valid"] + results["failed"]:
            test_info.append(f'This is a count mismatch in request -- missing {results["invoke"] - results["valid"] - results["failed"]} response(s)')
        else:
            test_info.append("")
        final_result = ",".join(test_info) + "\n"
    else:
        final_result = ",".join(test_info + [""] * 11 + [results["error"]]) + "\n"

    with open(REPORT_FILE, "a") as f:
        f.write(final_result)


def log_parser(log_file_path, encoding="utf8", extra_ids=None, extra_counts=None, extra_time=None, extra_details=None):
    """
    Return ??? when successfully parsing the log file. Return ??? when any errors.
    """
    log_file = open(log_file_path, "r", encoding=encoding)

    # 1. Parse start time in 1st line
    start_time = parse_time(log_file.readline())
    # 2. Parse test options in 2nd line
    test_args = parse_test_options(log_file.readline(), extra_ids=extra_ids)

    # 3. loop until start of the actual test
    if not loop_until(log_file, lambda l: "Relative time begins now" in l):
        print("\tThis test seems didn't reach the actual testing part.")
        return (test_args, {"error": "This test seems didn't reach the actual testing part."}) # TODO: need to refine 

    # 4. start processing
    # Get indication for nemesis based on nemesis type
    (nem_start_signs, nem_stop_signs) = get_nemesis_sign(test_args["nemesis"])
    test_results = processing_test(log_file, test_args["nemesis"], nem_start_signs, nem_stop_signs, test_args["workload"])
    if test_results is None:
        print("\tThis test seems didn't finish the actual testing part.")
        return (test_args, {"error": "This test seems didn't finish the actual testing part."}) # TODO: need to refine

    # 5. loop to finish
    finish_time = None
    if not loop_until(log_file, lambda l: "Analysis complete" in l):
        print("\tThis test seems didn't reach the very end.")
        return (test_args, {"error": "This test seems didn't reach the very end."}) # TODO: need to refine
    else:
        # Read 2 line to find the finish time
        line = log_file.readline()
        line = log_file.readline()
        whole_finished = True
        finish_time = parse_time(line)
        test_results["runtime"] = f"{round((finish_time - start_time).total_seconds(), 2)} s"
    
    # 6. loop to end
    if not loop_until(log_file, lambda l: "Everything looks good!" in l):
        # last line should be either "Everyhing looks good" or "invalid"
        verify_result = "Invalid"
    else:
        verify_result = "Valid"
    test_results["verify_result"] = verify_result


    return (test_args, test_results)


if __name__ == "__main__":
    # 1. Parse command line arguement
    cmd_parser()
    # 2. Get folder list
    workload_list = get_folder_list(RESULT_ROOT_FOLDER)
    # 3. Set up header line in the report
    set_csv_header(extra_ids=EXTRA_IDENTIFIERS)
    # 4. Process result 1 by 1
    for workload in workload_list:
        test_list = get_folder_list(f"{RESULT_ROOT_FOLDER}/{workload}")
        for current_test in test_list:
            print("Processing", workload, "-", current_test)
            # Analysis
            (args, results) = log_parser(f"{RESULT_ROOT_FOLDER}/{workload}/{current_test}/{LOG_FILE}", extra_ids=EXTRA_IDENTIFIERS)
            # Write
            append_to_csv(current_test, args, results)
            # print("\tFinish time:", finish_time.strftime(OUTPUT_TIME_FORMAT))
        #     break
        # break
