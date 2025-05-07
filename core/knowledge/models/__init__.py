# coding: utf-8

from knowledgeBase.models.data_model import *


for table in tables:
    table.create_table()
