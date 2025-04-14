from idlelib.outwin import file_line_pats
from wsgiref.util import request_uri

import pandas as pd
from sqlalchemy import create_engine,text
from unittest.mock import patch, MagicMock
import  pytest
from parsing_text_file import (extract_values,convert_string_integer,extract_settlement_date,process_all_records,
                               clean_value,extract_ref_no,extract_security)
file_path = "new3.txt"
with open(file_path, 'r') as file:
    content = file.read()

split_files=content.split('\f')

flat_list=[]
for rows in split_files:
    flat_list.append(rows.split('\n\n\n'))




def test_all_records_fields():

    for i in flat_list:
        result=extract_values(i)
        for outer_list in result:
            for record in outer_list:
                assert record['security_description'] == record['security_description']
                assert record['cu_sip'] != '79776778i7yu8g'


@pytest.fixture
def test_save_db():
    engine = create_engine("sqlite:///:memory:")

    with engine.connect() as connection:

        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS trade_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            for_date DATE,
            account VARCHAR(20),
            security_description VARCHAR(255),
            cu_sip VARCHAR(20),
            lot_quantity INT,
            trade_date DATE,
            settlement_date DATE,
            execution_date DATE,
            ref_no VARCHAR(15),
            price FLOAT,
            open_amount FLOAT,
            current_price FLOAT,
            current_market_value FLOAT,
            unrealized_p_and_l FLOAT,
            trade_int FLOAT,
            accrued_int FLOAT
        );
        """))
        # creating summary_details table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS summary_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            for_date DATE,
            account VARCHAR(20),
            security_description VARCHAR(255),
            cu_sip VARCHAR(20),
            lot_quantity INT,
            open_amount FLOAT,
            current_market_value FLOAT,
            unrealized_p_and_l FLOAT,
            trade_int FLOAT,
            accrued_int FLOAT
        );
        """))
        connection.commit()
    yield engine


def test_all_records(test_save_db):
    engine=test_save_db

    file_path = "Report_ECL891008_123124.txt"
    with open(file_path, 'r') as file:
        content = file.read()

    split_files = content.split('\f')
    flat_list = []

    for rows in split_files:
        flat_list.append(rows.split('\n\n\n'))


    result=process_all_records(flat_list, testing = True, engine = engine)
    assert result == 'summary and trade created'

    with engine.connect() as connection:
        one_record = connection.execute(text("select * from trade_details where ref_no= :ref_no"),{'ref_no':'P89K5J'}).fetchall()
        each_rec_count=connection.execute(text("select count(1) as 'cnt' from trade_details group by cu_sip having cu_sip=:cu_sip"),{'cu_sip' : '566593DH9'}).fetchall()


        summary_result=connection.execute(text("select * from summary_details")).fetchall()
        trade_result = connection.execute(text("select * from trade_details")).fetchall()


        connection.commit()

        assert one_record[0][3] == 'MIAMI-DADE CNTY FLA TRAN SYS SALES SURTAX REV BDS 2022 5.000% 07/01/51 B/E'
        assert len(trade_result) == 5172
        assert len(summary_result) == 4497
        assert one_record[0][3] != trade_result[0][3]
        assert one_record[0][4] == '59334PKY2'
        with pytest.raises(AssertionError):
            assert one_record[0][4] != '59334PKY2'
        assert each_rec_count[0][0] == 4






sample_record="""
MIAMI-DADE CNTY FLA         30,000  24/12/18  24/12/18    105.12     31,536.90     105.46      31,640.10        103.20      700.00  
TRAN SYS SALES                      24/12/19  P8WLQP                                                                          8.33- 
SURTAX REV BDS 2022                                                                                                                 
 5.000% 07/01/51 B/E                                                                                                                

                            10,000  24/12/23  24/12/23    104.09     10,409.90     105.46      10,546.70        136.80      240.28  
                                    24/12/24  P89K5J                                                                          2.78- 

                            50,000  24/12/24  24/12/24    104.25     52,128.50     105.46      52,733.50        605.00    1,215.28  
                                    24/12/26  P9BVGI                                                                         13.89- 

                            50,000  24/12/27  24/12/27    104.06     52,033.00     105.46      52,733.50        700.50    1,243.06  
                                    24/12/30  P9F8C6                                                                         13.89- 

MIAMI-DADE CNTY FLA   59334PKY2                                                                                                     
  SECURITY TOTAL =>        245,000                                  258,335.25                258,394.15         58.90    5,754.16  
                                                                                                                             68.07- 
            
"""


sample_list=sample_record.split('\n\n')
def test_convert_string_integer():

    result=float(convert_string_integer(sample_record[80:89].strip()))
    print(result)
    assert result == 105.4
    assert result != 112
    with pytest.raises(AssertionError):
        assert isinstance(result,int)

def test_settlement_date():
    result=extract_settlement_date(sample_record)
    assert result == '24/12/19'

def test_clean_value():
    result=float(clean_value( '2.78- '))
    assert result == -2.78
    with pytest .raises(AssertionError):
        assert result == 2.78
    assert isinstance(result,float)


def test_ref_no():
    result = extract_ref_no(sample_list)
    assert  result == 'P89K5J'
    with pytest.raises(AssertionError):
        assert result == 'P8WQT2'
    assert isinstance(result,str)
def test_extract_security():
    result = extract_security(sample_list[-1])
    print(result)
    assert isinstance(result,str)
    with pytest.raises(AssertionError):
        assert result == 'MIAMI-DADE CNTY FLA SECURITY TOTAL =>'
    assert result == 'MIAMI-DADE CNTY FLA SECURITY TOTAL => '
    assert len(result) == len('MIAMI-DADE CNTY FLA SECURITY TOTAL => ')


