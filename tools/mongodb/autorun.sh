#!/bin/bash

# for dqlite
# nemesis=('none' 'kill' 'partition' 'pause' 'member' 'stop')
# workloads=('append' 'set' 'bank')

# for Mongodb
nemesis=('pause' 'kill' 'partition' 'clock' 'member')
workloads=('list-append')
time_limit=300
nemesis_interval=60
rate=1000


for w in "${workloads[@]}"; do
    echo "Start processing for workload $w"
    for n in "${nemesis[@]}"; do
        # echo "    $n"
        for i in {1..3}; do
            # echo "$n $i"
            # # For dqlite
            # lein run test --workload $w --nemesis $n --time-limit $time_limit --test-count 1 --concurrency 2n --nemesis-interval $nemesis_interval
            # For MongoDB
            lein run test --nodes-file ~/nodes --workload $w --nemesis $n --time-limit $time_limit --test-count 1 --concurrency 3n --nemesis-interval $nemesis_interval --txn-read-concern snapshot --txn-write-concern majority --max-writes-per-key 128 --read-concern majority --write-concern majority --txn-read-concern snapshot --txn-write-concern majority -r $rate
            printf "\n\n\n"
        done
    done
done