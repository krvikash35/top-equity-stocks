import cherrypy, os
from redis import Redis
from bhavcopy import scheduleUpdate

root_dir = os.path.dirname(os.path.realpath(__file__))
index_file = os.path.join(root_dir, 'static', 'index.html')
static_dir = os.path.join(root_dir, 'static')

redisdb_host = 'redis-15164.c10.us-east-1-3.ec2.cloud.redislabs.com'
redisdb_port = '15164'
redisdb_name = 'redislabs'
redisdb_password = 'yzh4XKFdAtRQwLYG3riww5X7hDpOxdW0'
redis_conn = Redis(host=redisdb_host, port=redisdb_port, password=redisdb_password)

class STATIC(object):
    @cherrypy.expose
    def index(self):
        return file(index_file)

class API:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def topstocks(self):
        top_stocks_id = redis_conn.zrange('bhavcopy:equity:sccode:score', 0, 10, desc=True)
        top_stocks = []
        for stock_id in top_stocks_id:
            stock_details = redis_conn.hgetall('bhavcopy:equity:sccode:'+stock_id)
            top_stocks.append(stock_details)
        return top_stocks

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def searchstocks(self, name=""):
        stocks_details = []
        for sccode in redis_conn.hscan_iter('bhavcopy:equity:scname:sccode', match='*'+name+'*', count=10):
            print sccode
            stock_details = redis_conn.hgetall('bhavcopy:equity:sccode:'+sccode[1])
            stocks_details.append(stock_details)
        return stocks_details

root = STATIC()
root.api = API()

if __name__ == '__main__':
    cp_config = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': static_dir
        }
    }
    cherrypy.config.update({'server.socket_port': os.environ['PORT']})
    cherrypy.quickstart(root, '/', cp_config)
    scheduleUpdate()
