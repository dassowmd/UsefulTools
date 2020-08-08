# Source - Ben H
from scipy.stats import t
import pandas as pd
import numpy as np
import matplotlib

# pop = np.random.normal(10, 1, 100000)
# pop_samp = np.random.choice(pop, 50, replace = False)

# Statistically
def confidence_interval(x):
    n = len(x)  # sample size
    samp_mean = np.mean(x)  # sample mean
    st_dev = np.std(
        x, ddof=1
    )  # sample standard deviation, not you need to account for the standard devation of the sample
    st_err = st_dev / np.sqrt(n)  # standard error of the sample mean
    ci = t.ppf(0.975, n - 1) * st_err  # confidence interval bounds
    LCL = samp_mean - ci  # lower confidence interval
    UCL = samp_mean + ci  # upper confidence interval
    results = {
        "UCL": UCL,
        "sample_mean": samp_mean,
        "LCL": LCL,
    }  # compile to a dictionary
    return results  # print the dictionary


# Computationally
def sampling_eng(x, n_samples=100000):
    results = []  # empty list to collect data
    n = len(x)  # sample size
    samp_range = range(1, n_samples)  # sampling range
    for i in samp_range:
        samp = np.random.choice(x, n, replace=True)  # sample with replacement
        samp_mean = np.mean(samp)  # mean of samples
        results.append(samp_mean)  # append the results to a list
    results_mu = np.mean(results)  # caculcate the sample of resamples mean
    results_sd = np.std(
        results, ddof=1
    )  # calculate the standard deviation of the resamples
    UCL = results_mu + (2 * results_sd)  # two standard deviations up
    LCL = results_mu - (2 * results_sd)  # two standard deviations down
    results_dict = {
        "UCL": UCL,
        "sample_mean": samp_mean,
        "LCL": LCL,
    }  # compile to a dictionary
    return results_dict  # print the dictionary


i = 1
while i < 10:
    pop = np.random.normal(10, 1, 100000)
    pop_samp = np.random.choice(pop, 50, replace=False)
    # Call Statistic method
    print "Confidence Interval Method: " + str(confidence_interval(pop_samp))
    # Call Computational method
    print "Computational Method: " + str(sampling_eng(pop_samp, 750000))
    i += 1
