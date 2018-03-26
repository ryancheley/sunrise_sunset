import requests
import bs4
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


def main(city, state):
    city = city.replace(' ', '%20')
    source_data = [[0] * 25 for i in range(31)]
    url = 'http://aa.usno.navy.mil/cgi-bin/aa_rstablew.pl?ID=AA&year=2018&task=0&state={}&place={}'.format(state, city)
    city = city.replace('%20', ' ')
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    table = soup.find('pre')
    data = table.text.replace('\n', ' ').replace('  ', ' ').replace('       ','   ').split(' ')

    get_long_lat = (data.index('Location:'))

    sort_name = ['_'.join(data[get_long_lat+3:get_long_lat+5])][0]

    find_rise = data.index('Rise')

    data = data[find_rise:]

    row_01 = data.index('01')
    row_29 = data.index('29')
    row_30 = data.index('30')
    row_31 = data.index('31')
    for i in range(28):

        for j in range(25):
            if data[row_01+i*25+j]:
                source_data[i][j] = data[row_01+i*25+j]

    for j in range(25):
        if data[row_29+j]:
            source_data[28][j] = data[row_29+j]

    for j in range(25):
        if data[row_30+j]:
            source_data[29][j] = data[row_30+j]

    for j in range(25):
        if data[row_31+j]:
            source_data[30][j] = data[row_31+j]

    df = pd.DataFrame(source_data)

    final_data = []

    for i in range(int((df.shape[1]-1)/2)):
        month = '0' + str(i + 1)
        for j in range(df.shape[0]):
            if df[2*i+1][j] != 0:
                final_data.append('2018-'+month[-2:]+'-'+df[0][j]+' '+df[2*i+1][j]+' '+df[2*i+2][j])

    days = []
    rises = []
    sets = []
    for line in final_data:
        d, r, s = line.split()
        days.append(parse(d))
        hr, min = int(r[:2]), int(r[-2:])
        rises.append(hr + min/60)
        hr, min = int(s[:2]), int(s[-2:])
        sets.append(hr + min/60)

    # Daylight lengths
    lengths = np.array(sets) - np.array(rises)

    # Get the portion of the year that uses CDT
    if state != 'AZ':
        cdtStart = days.index(datetime(2018, 3, 11))
        cstStart = days.index(datetime(2018, 11, 4))
        cdtdays = days[cdtStart:cstStart]
        cstrises = rises[cdtStart:cstStart]
        cdtrises = [x + 1 for x in cstrises]
        cstsets = sets[cdtStart:cstStart]
        cdtsets = [x + 1 for x in cstsets]

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.fill_between(days, rises, sets, facecolor='yellow', alpha=.5)
    plt.fill_between(days, 0, rises, facecolor='black', alpha=.25)
    plt.fill_between(days, sets, 24, facecolor='black', alpha=.25)
    if state != 'AZ':
        plt.fill_between(cdtdays, cstsets, cdtsets, facecolor='yellow', alpha=.5)
        plt.fill_between(cdtdays, cdtrises, cstrises, facecolor='black', alpha=.1)
    plt.plot(days, rises, color='k')
    plt.plot(days, sets, color='k')
    if state != 'AZ':
        plt.plot(cdtdays, cdtrises, color='k')
        plt.plot(cdtdays, cdtsets, color='k')
    plt.plot(days, lengths, color='#aa00aa', linestyle='--', lw=2)
    plt.title('{}, {}'.format(city, state))

    # Add annotations
    ax.text(datetime(2018, 8, 16), 4.25, 'Sunrise', fontsize=12, color='black', ha='center', rotation=9)
    ax.text(datetime(2018, 8, 16), 18, 'Sunset', fontsize=12, color='black', ha='center', rotation=-10)
    ax.text(datetime(2018, 3, 16), 13, 'Daylight', fontsize=12, color='#aa00aa', ha='center', rotation=22)

    # Background grids
    ax.grid(linewidth=1, which='major', color='#cccccc', linestyle='-', lw=.5)
    ax.grid(linewidth=1, which='minor', color='#cccccc', linestyle=':', lw=.5)

    # Horizontal axis
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.xlim(datetime(2018, 1, 1), datetime(2018, 12, 31))
    m = mdates.MonthLocator(bymonthday=1)
    mfmt = mdates.DateFormatter('              %b')
    ax.xaxis.set_major_locator(m)
    ax.xaxis.set_major_formatter(mfmt)

    # Vertical axis
    plt.ylim(0, 24)
    ymajor = MultipleLocator(4)
    yminor = MultipleLocator(1)
    tfmt = FormatStrFormatter('%d:00')
    ax.yaxis.set_major_locator(ymajor)
    ax.yaxis.set_minor_locator(yminor)
    ax.yaxis.set_major_formatter(tfmt)

    # Tighten up the white border and save
    fig.set_tight_layout({'pad': 1.5})
    plt.savefig('{}_{}_{}_rise_set_chart.png'.format(sort_name, city, state), format='png', dpi=150)


if __name__ == '__main__':
    main('Portland', 'OR')

'''
    Eugene, OR [X]
    Salem, OR [X]
    Seaside, OR [X]
    ---
    Eureka, CA
    Indio, CA
    Long Beach, CA
    Monterey, CA
    San Diego, CA
    San Francisco, CA
    San Luis Obispo, CA
    Ventura, CA
    ---
    Ferndale, WA
    Olympia, WA
    Seattle, WA
'''