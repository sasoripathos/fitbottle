
import matplotlib.pyplot as plt
import numpy as np

# # Sample data (each sublist represents a group of data, each element in sublist is a sub-category)
# data = [
#     [20, 22, 24],   # Group 1
#     [40, 42, 44],   # Group 2
#     [55, 56, 54],   # Group 3
#     [33, 34, 32],   # Group 4
#     [21, 22, 23]    # Group 5
# ]

# # Calculate the mean and standard deviation for each sub-category
# means = [np.mean(group) for group in data]
# std_devs = [np.std(group) for group in data]

def draw_bar(data_avgs, data_mins, data_maxs, bar_width, group_labels, case_labels, title, xlable, explanation):
    fig, ax = plt.subplots()
    # Range for groups
    x = np.arange(len(group_labels))
    # Plot each sub-category as separate bars
    for i in range(len(case_labels)):
        means = data_avgs[i]
        mins = data_mins[i] if len(data_mins) > 0 else []
        maxs = data_maxs[i] if len(data_maxs) > 0 else []
        ax.bar(x + i * bar_width, means, bar_width, label=case_labels[i], capsize=5)
        # Add min max
        if len(data_mins) > 0:
            for j in range(len(group_labels)):
                ax.errorbar(x[j] + i * bar_width, means[j], yerr=[[means[j] - mins[j]], [maxs[j] - means[j]]], color='black', capsize=5)
    # Set title and labels
    ax.set_title(title, fontweight='bold', fontsize=15)
    ax.set_xlabel(xlable, fontweight='bold', fontsize=13)
    ax.set_ylabel('Time (second)', fontweight='bold', fontsize=13)
    ax.set_xticks(x + bar_width * (len(case_labels) - 1) / 2)
    ax.set_xticklabels(group_labels)
    # ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
    ax.legend()
    # plt.ylim(0, 7.5)
    plt.axhline(y=12, color='r', linestyle='--', label='12 Seconds')

    # Add explanation text
    # plt.figtext(0.5, 0.01, explanation, wrap=True, horizontalalignment='center', fontsize=10)
    plt.show()

# Figrue 1 -- kill, vary rate and interval, rate 10 1000 10 1000, interval 10 10 60 60, with data
major_read_avg = [1.271, 3.812, 3.274, 1.686]
major_read_max = [2.634, 5.286, 4.479, 3.66]
major_read_min = [0.198, 2.862, 2.33, 0.623]
major_read_div = [1.244, 1.294, 1.098, 1.711]

major_write_avg = [4.22, 4.531, 4.183, 4.684]
major_write_max = [4.377, 5.337, 4.479, 5.066]
major_write_min = [3.998, 4.072, 3.666, 4.199]
major_write_div = [0.198, 0.7, 0.449, 0.443]


group_labels = ["R=10, I=10", "R=1000, I=10", "R=10, I=60", "R=1000, I=60"]
case_labels = ['Time to first successful read', 'Time to first successful write']
# draw_bar([major_read_avg, major_write_avg], [major_read_min, major_write_min], [major_read_max, major_write_max], 0.2, group_labels, case_labels,
#     "Time between recovery start to first successful read/write request", # set_title
#     'Combination of user request rate (R) and fault interval (I)', # set_xlabel
#     'Each bar represents the average of 3 measurements in a test run, while the error bars represents the max and min of 3 measurements in a test run.' # explanation
# )


# Figure 2 -- majority, all data, reconfig
major_read_avg = [4.338, 4.082, 4.089, 3.143]
major_read_max = [5.547, 5.12, 4.205, 3.504]
major_read_min = [3.316, 3.035, 3.867, 2.786]
major_read_div = [1.127, 1.043, 0.193, 0.359]

major_write_avg = [5.542, 4.752, 5.152, 5.676]
major_write_max = [5.811, 5.12, 5.771, 6.197]
major_write_min = [5.267, 4.091, 4.205, 5.362]
major_write_div = [0.272, 0.573, 0.833, 0.454]
group_labels = ["Run 1", "Run 2", "Run 3", "Run 4"]
case_labels = ['Time to first successful read', 'Time to first successful write']
# draw_bar([major_read_avg, major_write_avg], [major_read_min, major_write_min], [major_read_max, major_write_max], 0.2, group_labels, case_labels,
#     "Time between recovery start to first successful read/write request", # set_title
#     'Test Runs with user request rate R=10, fault interval I=1000', # set_xlabel
#     'Each bar represents the average of 3 measurements in a test run, while the error bars represents the max and min of 3 measurements in a test run.' # explanation
# )

# Figure 3 -- primary, all data, reconfig
major_1_avg = [3.628, 0.625, 2.837, 0.519]

major_2_avg = [11.38, 11.292, 12.81, 11.684]

major_3_avg = [11.265, 1.739, 11.22, 11.32]

group_labels = ["Run 1", "Run 2", "Run 3", "Run 4"]
case_labels = ['Cycle 1', 'Cycle 2', "Cycle 3"]
draw_bar([major_1_avg, major_2_avg, major_3_avg], [], [], 0.2, group_labels, case_labels,
    "Time between the start of fault injection to the end of continuous write request failure", # set_title
    'Measurements for 3 cycles for each test run, with user request rate R=10, fault interval I=1000', # set_xlabel
    'Each bar represents the average of 3 measurements in a test run, while the error bars represents the max and min of 3 measurements in a test run.' # explanation
)



# Figure 4 -- majority, no data, reconfig
major_read_avg = [5.998, 3.081, 1.041, 4.282]
major_read_max = [6.334, 5.221, 2.07, 6.249]
major_read_min = [5.331, 0.54, 0.36, 0.38]
major_read_div = [0.578, 2.366, 0.906, 3.379]

major_write_avg = [6.089, 5.127, 5.246, 5.993]
major_write_max = [6.597, 6.677, 6.878, 6.515]
major_write_min = [5.337, 3.482, 3.517, 5.216]
major_write_div = [0.665, 1.6, 1.681, 0.686]
group_labels = ["Run 1", "Run 2", "Run 3", "Run 4"]
case_labels = ['Time to first successful read', 'Time to first successful write']
# draw_bar([major_read_avg, major_write_avg], [major_read_min, major_write_min], [major_read_max, major_write_max], 0.2, group_labels, case_labels,
#     "Time between recovery start to first successful read/write request", # set_title
#     'Test Runs with user request rate R=10, fault interval I=1000', # set_xlabel
#     'Each bar represents the average of 3 measurements in a test run, while the error bars represents the max and min of 3 measurements in a test run.' # explanation
# )


# major_allgood_avg = [4.629, 8.179, 4.75, 12.02]
# major_allgood_min = [3.002, 8.026, 2.697, 3.148]
# major_allgood_max = [7.877, 8.47, 7.912, 24.373]
# major_allgood_div = [2.813, 0.252, 2.779, 11.033]


# minor_read_avg = [1.271]
# minor_read_div = [1.244]
# minor_write_avg = [4.22]
# minor_write_div = [0.198]
# minor_allgood_avg = [4.629]
# minor_allgood_div = [2.813]

# prim_read_avg = [1.271]
# prim_read_div = [1.244]
# prim_write_avg = [4.22]
# prim_write_div = [0.198]
# prim_allgood_avg = [4.629]
# prim_allgood_div = [2.813]


# # Number of groups and sub-categories
# n_groups = len(data)
# n_subcategories = len(data[0])

# # Labels for the bars
# group_labels = ['A', 'B', 'C', 'D', 'E']
# subcategory_labels = ['X', 'Y', 'Z']

# # Creating an array for x locations
# x = np.arange(n_groups)

# # Width of the bars
# bar_width = 0.2

# # Create figure and axis
# fig, ax = plt.subplots()

# # Plot each sub-category as separate bars
# for i in range(n_subcategories):
#     means = [group[i] for group in data]
#     std_devs = [np.std(group) for group in data]
#     mins = [min(group) for group in data]
#     maxs = [max(group) for group in data]
#     ax.bar(x + i * bar_width, means, bar_width, label=subcategory_labels[i], capsize=5) # Add error bars for min and max values
#     for j in range(n_groups):
#         ax.errorbar(x[j] + i * bar_width, means[j], yerr=[[means[j] - mins[j]], [maxs[j] - means[j]]], fmt='o', color='black', capsize=5)

# # Set title and labels
# ax.set_title('Grouped Bar Chart with Error Bars')
# ax.set_xlabel('Groups')
# ax.set_ylabel('Values')
# ax.set_xticks(x + bar_width * (n_subcategories - 1) / 2)
# ax.set_xticklabels(group_labels)
# ax.legend()

# # Display the plot
# plt.show()

