from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, analyzer, InnerDoc, Completion, Integer, Boolean, Keyword, Text
from elasticsearch_dsl.connections import connections

import elasticsearch as elastic

# Es 默认连接, Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'], timeout=20)


class BaseStock(Document):
    ts_code = Keyword()  # TS代码
    symbol = Keyword()  # 股票代码
    name = Keyword()  # 股票名称
    area = Text(fields={'raw': Keyword()})  # 所在地域
    industry = Keyword()  # 所属行业
    fullname = Keyword()  # 股票全称
    enname = Keyword()  # 英文全称
    market = Keyword()  # 市场类型 （主板 / 中小板 / 创业板）
    exchange = Keyword()  # 交易所代码
    curr_type = Keyword()  # 交易货币
    list_status = Keyword()  # 上市状态： L上市、D退市、P暂停上市
    list_date = Date()  # 上市日期
    delist_date = Date()  # 退市日期
    is_hs = Keyword()  # 是否沪深港通标的，N否、H沪股通、 S深股通
    timestamp = Date()  # 创建时间

    class Index:
        name = 'stock-list'
        settings = {
            "number_of_shards": 2,
        }

    def save(self, **kwargs):
        # assign now if no timestamp given
        if not self.timestamp:
            self.timestamp = datetime.now()
        # override the index to go to the proper timeslot
        #kwargs['index'] = self.timestamp.strftime('stock-list-%Y%m%d')
        return super(BaseStock, self).save(**kwargs)


# # create the mappings in elasticsearch
# BaseStock.init()
#
# # create and save and article
# stock = BaseStock(meta={'id': 42}, title='Hello world!', tags=['test'])
# stock.body = ''' looong text '''
# stock.published_from = datetime.now()
# stock.save()


# 连接本地ES
# es = elastic.Elasticsearch("localhost:9200")
# if  not es.indices.exists('my-stock') :
#     es.indices.create(index='my-stock', ignore=400)



# es.index('my-stock',"indexType",jsonArray);

# es.bulk(index="my-stock",doc_type="indexType",body=[{"any":"data02","timestamp":datetime.now()},{"any":"data03","timestamp":datetime.now()}])