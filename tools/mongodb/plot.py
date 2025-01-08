
import matplotlib.pyplot as plt
import numpy as np

# Sample data (each sublist represents a group of data, each element in sublist is a sub-category)
data = [
    [20, 22, 24],   # Group 1
    [40, 42, 44],   # Group 2
    [55, 56, 54],   # Group 3
    [33, 34, 32],   # Group 4
    [21, 22, 23]    # Group 5
]

# Calculate the mean and standard deviation for each sub-category
means = [np.mean(group) for group in data]
std_devs = [np.std(group) for group in data]

def draw_bar(data_avgs, data_mins, data_maxs, bar_width, group_labels, case_labels, title, xlable, explanation):
    fig, ax = plt.subplots()
    # Range for groups
    x = np.arange(len(group_labels))
    # Plot each sub-category as separate bars
    for i in range(len(case_labels)):
        means = data_avgs[i]
        mins = data_mins[i]
        maxs = data_maxs[i]
        ax.bar(x + i * bar_width, means, bar_width, label=case_labels[i], capsize=5)
        # Add min max
        for j in range(len(group_labels)):
            ax.errorbar(x[j] + i * bar_width, means[j], yerr=[[means[j] - mins[j]], [maxs[j] - means[j]]], color='black', capsize=5)
    # Set title and labels
    ax.set_title(title, fontweight='bold', fontsize=15)
    ax.set_xlabel(xlable, fontweight='bold', fontsize=13)
    ax.set_ylabel('Time', fontweight='bold', fontsize=13)
    ax.set_xticks(x + bar_width * (len(case_labels) - 1) / 2)
    ax.set_xticklabels(group_labels)
    ax.legend()

    # Add explanation text
    # plt.figtext(0.5, 0.01, explanation, wrap=True, horizontalalignment='center', fontsize=10)
    plt.show()

# Figrue 1 -- kill, vary rate and interval, rate 10 1000 10 1000, interval 10 10 60 60
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
draw_bar([major_read_avg, major_write_avg], [major_read_min, major_write_min], [major_read_max, major_write_max], 0.2, group_labels, case_labels,
    "Time between recovery start to first successful read/write request", # set_title
    'Combination of user request rate (R) and fault interval (I)', # set_xlabel
    'Each bar represents the average of 3 measurements in a test run, while the error bars represents the max and min of 3 measurements in a test run.' # explanation
)



# Figure 2 -- majority, no remove
avg:4.067; max:5.013; min:2.615; sd:1.277;	avg:4.417; max:5.013; min:3.663; sd:0.689;


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

