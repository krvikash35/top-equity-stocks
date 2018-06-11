from zipfile import ZipFile
from datetime import datetime, timedelta
from redis import Redis 
import requests, os, csv, schedule, time, threading

os.environ['TZ']='Asia/Kolkata'
time.tzset()

root_dir = os.path.dirname(os.path.realpath(__file__))
download_dir = os.path.join(root_dir, 'download')
extract_dir = os.path.join(root_dir, 'extract')
redisdb_host = 'redis-15164.c10.us-east-1-3.ec2.cloud.redislabs.com'
redisdb_port = '15164'
redisdb_name = 'redislabs'
redisdb_password = 'yzh4XKFdAtRQwLYG3riww5X7hDpOxdW0'

def delete_dir_files(folder):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)


def download():
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
    else:
        delete_dir_files(download_dir)
    
    print('Download folder: %s\nExtract folder: %s' %(download_dir, extract_dir))


    latest_bhavcopy_file = 'EQ' + datetime.now().strftime('%d%m%y') + '_CSV.ZIP'
    # latest_bhavcopy_file = 'EQ080618_CSV.ZIP'
    download_url = 'https://www.bseindia.com/download/BhavCopy/Equity/' + latest_bhavcopy_file
    print('Download URL: %s' %(download_url))

    r = requests.get(download_url);
    if r.status_code == requests.codes.ok:
        download_file = os.path.join(download_dir, latest_bhavcopy_file)
        file = open(download_file, 'wb')
        file.write(r.content)
        print('Latest equity bhavcopy downloaded to file: %s' %(download_file))
        return download_file
    else:
        raise Exception('Error while downloading, response code from server: '+ str(r.status_code))



def extract(file_tobe_extracted):
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)
    else:
        delete_dir_files(extract_dir)

    file = ZipFile(file_tobe_extracted)
    file.extractall(extract_dir)
    file.close()
    extracted_file = os.path.join(extract_dir, file.namelist()[0])
    print('Latest equity bhavcopy extracted to file: %s' %(extracted_file))
    return extracted_file



def saveToRedisDB(file):
    redisConn = Redis(host=redisdb_host, port=redisdb_port, password=redisdb_password)
    redisConn.flushall()
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        # print('Number of records:%d' %(len(list(reader))))
        for row in reader:
            key = 'bhavcopy:equity:sccode:'+row['SC_CODE']
            value = {
                'code':  row['SC_CODE'],
                'name':  row['SC_NAME'],
                'open':  row['OPEN'],
                'high':  row['HIGH'],
                'low':   row['LOW'],
                'close': row['CLOSE']
            }
            redisConn.hmset(key, value)
            score = (( float(row['CLOSE']) - float(row['OPEN']) ) / float(row['OPEN']))*100
            redisConn.zadd('bhavcopy:equity:sccode:score', row['SC_CODE'], score)
            redisConn.hmset('bhavcopy:equity:scname:sccode', {row['SC_NAME']: row['SC_CODE']})
            print('Inserted record for %s' %(row['SC_CODE']))



def job():
    # Don't run job at weekends
    currentDay = datetime.now().strftime('%A')
    if currentDay == 'Saturday' or currentDay == 'Sunday':
        return
    try:
        downloaded_file = download()
        extracted_file = extract(downloaded_file)
        saveToRedisDB(extracted_file)
    except Exception as err:
        print('Error occured while performing job', err)


# Run this job every day at 6PM
# schedule.every().day.at("18:00").do(job)
schedule.every(1).seconds.do(job)



class ScheduleThread(threading.Thread):
    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(schedule.idle_seconds())




def scheduleUpdate():
    ScheduleThread().start()




# redis reference
# http://tylerstroud.com/2014/11/18/storing-and-querying-objects-in-redis/
# https://matt.sh/thinking-in-redis-part-one
# https://medium.com/@stockholmux/from-sql-to-redis-chapter-1-145c82e4baa0
# https://redis.io/topics/data-types
