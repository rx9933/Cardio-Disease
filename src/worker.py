import logging
import time
import json
from flask import Flask, request
import requests
from jobs import get_job_by_id, update_job_status, q, rd
import os
import redis
from math import ceil
import matplotlib.pyplot as plt
from textwrap import wrap

_redis_ip = os.environ.get('REDIS_IP','environment not found')
_redis_port = '6379'

res_db = redis.Redis(host=_redis_ip, port=6379, db=3)

# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

def return_topics(para:dict):
    '''
    Function returns the major topics the catagory Cardiovascular Diseases (stroke, acute myocardial infarction, etc.).
    Args:
        para: input parameters (all functions in worker.py (other than do_work) have this as input). For this function, para can be anything, including an empty dictionary.
    Returns:
        classkeys: a list of strings, where each string is a cardiovascular disease.
    '''
    logger.info("Getting topics")
    classkeys = []
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data["category"] == 'Cardiovascular Diseases':
            if data["topic"] in classkeys:
                pass
            else:
                classkeys += [data["topic"]]
    logger.info("Returning topics")
    return classkeys

def max_affected(para: dict):

    """
    Function returns the datum with the most percentage affected by the specified cardiovascular disease. 
    Args:
        para: input parameters dictionary. This can optionally contain the break_out type (an age category like 65+ or a gender like Male or a race like Hispanic), a location (like Arizona), and a specific cardiovascular disease (Stroke).
    Returns: the data dictionary with the maximum population percentage affected by the specified disease (if input) or a string that no data is found satisfying the specified inputs.
    """
    keys_input = ["topic", "year", "break_out"]
    keys_to_keep = [key for key in keys_input if para[key] != ""]
    maxpercent = None
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data["category"] == 'Cardiovascular Diseases':
            correct_type = all(data[spec] == para[spec] for spec in keys_to_keep)
            if correct_type and "data_value" in data:
                if maxpercent is None or float(data["data_value"]) > float(maxpercent["data_value"]):
                    maxpercent = data
    if maxpercent is None:
        return "No data of this type can be found to analyze.\n"
    return maxpercent

def test_work(para:dict):
    '''
    This is a test function that simulatees work by sleeping for 20 seconds.
    Args:
        para: input parameters (all functions in worker.py (other than do_work) have this as input). For this function, para can be anything, including an empty dictionary.
    Returns:
        output: a dictionary of an example output
    '''
    logger.info("Starting test work")
    time.sleep(20)
    output = {"random output parameter 1": "1st output parameter value"}
    logger.info("Finished test work")
    return output

def sort_data(para:dict):
    '''
    Given a set of parameters, this 
    '''
    return

def select_series(location:str, breakout:str, topic:str):
    '''
    Given a location, a topic, and breakout category, this function creates data for time vs data value series. Called on by rf_v_disease
    Args:
        para: input parameters. For this function parameters include breakout (str) (optional, default to overall), topic (str), lcoation (list)
    Returns:
        return_dict: The XY data for the graphs, X is the year, Y is the data value
        
    '''
    # What does return dict look like {X: Y}
    # loop through redis db, look for rd[key][location]
    # checks if the data value is between
    logger.info(f"Select series function started for {topic}")
    return_dict = {}
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data['data_value_typeid'] == 'Crude' and data['break_out_category'] != 'Age':
            continue
        if location == data['locationabbr'] or location == data['locationdesc']:
            indicator = data['indicator']
            indicator_trimmed = indicator.replace('Prevalence of ', '')
            indicator_trimmed = indicator_trimmed.split(' among')[0] 
            if topic.lower() == indicator_trimmed and breakout == data['break_out']:
                # checks if data value is statistically relevant
                # if not, log warning with data value notes
                year = data['year']
                try:
                    data_value = data['data_value']
                except KeyError:
                    logger.warning(f"No data value for {location}, {year}, {topic}, {breakout}: {data['data_value_footnote']}")
                    continue
                return_dict[year] = data_value
            else:
                continue
        else:
            continue
    logger.info(f"Select series function ended for topic {topic}")
    return return_dict

def graph_rf(para:dict):
    '''
    Given a location, a disease, a list of risk factors, and a breakout category, this function uses matplot lib to graph the disease and risk factor over time.
    Args:
        para (dict): This is a dictionary of parameters: 'breakout' (str) for break out (default to overall), 'disease' (str) for the disease, 'risk_factor' (list) for the list of risk factors, 'location' (lst) for the location (default to USM), and 'detrend' (str) which specifies whether the data should be detrended (default to False)
    '''
    risk_factors = para['risk_factors']
    disease = para['disease']
    # set the location default to USM
    if 'location' in para.keys():
        location = para['location']
    else:
        logger.warning(f"No paramerter was provided for location. Default to USM")
        location = 'Median of all states'
    #set the breakout to Overall if it does not exist
    if 'breakout' in para.keys():
        breakout = para['breakout']
    else:
        logger.warning(f"No parameter was provided for breakout category")
        breakout = 'Overall'
    # set the detrend to False if it does not exist
    if 'detrend' in para.keys():
        detrend = bool(para['detrend'])
    else:
        logger.warning(f"No parameter was provided for detrend")
        detrend = False

    ylabel = "Age Standardized Rate (%)"

    xy_data = {}
    risk_factors.append(disease)
    # loop through all risk factors and diseases to graph
    for risk_factor in risk_factors:
        rf_data = select_series(location=location, topic=risk_factor, breakout=breakout)
        # sort data and put in the correct type
        rf_sorted = {}
        for i in sorted(rf_data.keys()):
            rf_sorted[int(i)] = float(rf_data[i])
        if detrend:
            rf_sorted = detrend_data(rf_sorted)
            ylabel = "Detrended Age Standardized Rate (%)"
        label = f"Prevalence of {risk_factor.lower()} among US adults"
        xy_data[label] = rf_sorted 
    
    plot_data(xy_data=xy_data, title=f"Prevalence of {disease.title()} and Associated Risk Factors Among the {breakout} Population in {location.title()}", xlabel="Year", ylabel=ylabel)
    return

def detrend_data(xy_data:dict):
    '''
    Detrends data by subtracting the best fit y value from the real y value
    Inputs:
        xy_data (detrend): A dictionary of all data pairs

    Outputs:
        data_detrended (dictionary): A dictionary of all detrended data pairs
    '''
    detrended_data = {}
    x = list(xy_data.keys())
    y = list(xy_data.values())

    n = len(xy_data.keys())
    x_bar = sum(x) / n
    y_bar = sum(y) / n
    # Find the slope of linear best fit line
    num = 0
    denom = 0 
    for i in range(len(x)):
        num += (x[i] - x_bar)*(y[i] - y_bar)
        denom += (x[i] - x_bar)**2
    b = num / denom
    # Find intercept of best fit line
    a = y_bar - b*x_bar

    for x in xy_data.keys():
        # calculate y value at each x
        y_real = xy_data[x]
        y_expected = b*x + a
        # Subtract expected y value from real y value & add detrended value to the dictionary
        y_detrend = y_real - y_expected
        detrended_data[x] = y_detrend
    
    return detrended_data

def correlation(para:dict):
    '''
    Calculates the correlation between a risk factor and a disease
    Inputs:
        para (dict): This is a dictionary of parameters: 'breakout' (str) for break out (default to overall), 'disease' (str) for the disease, 'risk_factor' (list) for the list of risk factors, and 'location' (lst) for the location (default to USM)
    Outputs:
        result_dictionary (dict): This dictionary contains information regarding the correlation coefficient and other linear regression information 
    '''
    result_dictionary = {}

    # sort through the data like above
    risk_factors = para['risk_factors']
    disease = para['disease']
    # set the location default to USM
    if 'location' in para.keys():
        location = para['location']
    else:
        logger.warning(f"No paramerter was provided for location. Default to USM")
        location = 'Median of all states'
    #set the breakout to Overall if it does not exist
    if 'breakout' in para.keys():
        breakout = para['breakout']
    else:
        logger.warning(f"No parameter was provided for breakout category")
        breakout = 'Overall'
    
    # Select and type cast the series data
    dis_data = select_series(location=location, topic=disease, breakout=breakout)
    dis_sorted = {}
    for i in sorted(dis_data.keys()):
        dis_sorted[int(i)] = float(dis_data[i])
    dis_sorted = detrend_data(dis_sorted)

    # loop through all risk factors
    for risk_factor in risk_factors:
        rf_data = select_series(location=location, topic=risk_factor, breakout=breakout)
        # sort data and put in the correct type
        rf_sorted = {}
        for i in sorted(rf_data.keys()):
            rf_sorted[int(i)] = float(rf_data[i])
        # detrend the series
        rf_sorted = detrend_data(rf_sorted)
        
        # check if there is >5 similar data points bc rf_sorted and dis_sorted
        dis_years_set = set(dis_sorted.keys())
        rf_years_set = set(rf_sorted.keys())
        years_intersect = dis_years_set.intersection(rf_years_set)
        if len(years_intersect) < 5:
            logger.warning(f'Not enough data between risk_factor.lower() and disease.lower()')
            result_dictionary[f'Correlation coefficient between {risk_factor.lower()} and {disease.lower()}'] = "Not enough data"
        else:
            # calculate the correlation coefficent between the y values of the risk factor and the y value of the disease
            dis_rate = []
            rf_rate = []
            for year in years_intersect:
                dis_rate.append(dis_sorted[year])
                rf_rate.append(rf_sorted[year])
            correlation_coeff = calculate_correlation(dis_rate, rf_rate)

            result_dictionary[f'Correlation coefficient between {risk_factor.lower()} and {disease.lower()}'] = correlation_coeff

    return result_dictionary

def calculate_correlation(x:list, y:list):
    '''
    Calculates the correlation coefficient between two variables

    Inputs:
        x (list): Data points of one variable as integers or floats
        y (list): Data points of another variable as integers or floats, must be the same length as x
    Outputs:
        correlation_coeff (float): correlation coefficient between the two data

    '''
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_squared = sum([i**2 for i in x])
    sum_y_squared = sum([i**2 for i in y])
    n = len(x)

    sum_xy = 0
    for i in range(len(x)):
        sum_xy += (x[i] * y[i])

    num = n*sum_xy - sum_x*sum_y
    denom = ((n*sum_x_squared - sum_x**2) * (n*sum_y_squared - sum_y**2))**(1/2)
    
    correlation_coeff = num / denom

    return correlation_coeff

def graph_correlation(para:dict):
    '''
    Graphs the correlation between two variables.
    '''
    return

def plot_data(xy_data:dict, title:str, xlabel:str, ylabel:str):
    '''
    Given a list of series data, this function plots all data on the same graph it using matplotlib.
    Inputs:
        xy_data: A dictionary where the key is the label and the value is another dictionary of the actual data pairs
        title: A string that will be used for the title of the graph
        xlabel: A string that will be used to label the x axis
        ylabel: A string that will be used to label the y axis
    '''
    plt.close()
    
    graph_labels = []
    # for a each item in xy_data, plot the x and y values
    for key in xy_data.keys():
        xy = xy_data[key]
        plt.plot(xy.keys(), xy.values())
        graph_labels.append(key)
        logger.info(f"Plotted {xy.keys()} vs {xy.values()}")

    # plot info
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title, fontsize=10)
    logger.debug(f"graph labels = {graph_labels}")
    graph_labels = ['\n'.join(wrap(i, 25)) for i in graph_labels]
    plt.legend(graph_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
    
    # saving image to results db
    plt.savefig('/output_image.png', bbox_inches='tight')
    return

@q.worker
def do_work(jobid:str):
    '''
    Main function in worker.py. It calls different worker functions (each of which provides a certain type of analysis).
    Args:
        jobid: a string, which is the jobid of the particular job in the queue
    Returns:
        None: the function updates the job with the output data, and when users curl a get route, that information is displayed to the screen.
    '''
    logger.info(f"Starting job: {jobid}")
    update_job_status(jobid, 'in progress')
    job_desc = get_job_by_id(jobid)
    functName = job_desc["function_name"]
    input_para = job_desc["input_parameters"]

    output = eval(functName)(input_para)
    # opening image and saving in redis
    if functName == 'graph_rf':
        with open('/output_image.png', 'rb') as f:
            img = f.read()
        res_db.set(jobid, img)
    else:
        res_db.set(jobid, json.dumps(output))
    status = "complete"
    update_job_status(jobid, status)
    logger.info(f"Finished job: {jobid}")

if __name__ == '__main__':
    do_work()

































































