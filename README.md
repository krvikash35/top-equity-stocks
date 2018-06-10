# top-equity-stocks
Get top equity stocks based on day end trading statitics along with search fuctionality. Everyday at `6PM IST` database is updated with
latest Equity Bhavcopy from [bseindia](http://www.bseindia.com/markets/equity/EQReports/BhavCopyDebt.aspx?expandable=3)

# Demo
This application has been deplyoed to `heroku`. you can acces it at [this link](https://top-equity-stocks.herokuapp.com/). Has been tested on latest Chrome and Safari.

# Back-end
There are two main python file `bhavcopy.py` and `server.py`.

`bhavcopy.py` contain below functions:
    
1. Latest bhavcopy file name logic
2. Download latest bhavcopy zip file
3. Extract zip file to CSV file
4. Parse CSV file and save the record to redis database using appropriate data structure
6. Threaded Funtion to run above steps at every `Weekdays` at `6PM IST`

`server.py` contains below functions:

1. Serve static files to fulfill front-end part
2. Serve API endpoint that fetches data from redis database

# Front-end
Front-end logic has been written in folder `static`. Using `React.JS` for UI/Data management and `requests` for http request/response. Following feature has been implemented.

1. Search equity details by name, name need not be exact full name, search is performed using containing word.
2. Display top 10 stocks on the basis of %change in price
