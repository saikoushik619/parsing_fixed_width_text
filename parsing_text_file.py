import pandas as pd

import time
from sqlalchemy import create_engine,text


file_path = "Report_ECL891008_123124.txt"

def extract_summary_accrued(record):
    m=record.split('\n')
    sum_acc=[]
    for i in range(0,len(m)):
        if i==2:
            sum_acc.append(m[i][120:131].strip())
    return ''.join(sum_acc)

def extract_security(record):
    lines = []
    security=record.split('\n')

    for line in range(0,len(security)):
        if security[line].strip()!='':

            lines.append(security[line][0:20].strip())


    return " ".join(lines)

#extract dates
def extract_settlement_date(sd_date):
    dates=[]
    sd_dates=sd_date.split('\n')
    for rec in range(len(sd_dates)):
        if rec==1:
            dates.append(sd_dates[rec][36:44].strip())


    return " ".join(dates)
def extract_ref_no(data):
    ref_no=[]
    rf_number=data.split('\n')
    for rec in range(len(rf_number)):
        if rec==1:
            ref_no.append(rf_number[rec][45:54].strip())
    return ''.join(ref_no)


#extract accured int
def extract_a_val(record):
    a_int=record.split('\n')

    acc_num=[]
    sum_acc=[]
    for acc_int in range(0,len(a_int)):
        if len(a_int)==3:
            if acc_int==2:
                sum_acc.append(a_int[acc_int][120:131].strip())


        elif len(a_int)>3:
            if acc_int==1:
                acc_num.append(a_int[acc_int][120:131].strip())

        else:
            acc_num.append(a_int[acc_int][120:131].strip())
    return ''.join(acc_num)


def clean_value(value):

    value = value.strip()


    decimal_count = 0
    sanitized_value = ''
    negative_in_middle = False


    for i, char in enumerate(value):
        if value=='':
            sanitized_value=None
        if char.isdigit() or char == '-':

            if char == '-' and i != 0 and value[i-1].isdigit():
                negative_in_middle = True
                continue
            sanitized_value += char
        elif char == '.':

            if decimal_count == 0:
                sanitized_value += char
                decimal_count += 1
        else:

            continue


    if negative_in_middle:

        sanitized_value = '-' + sanitized_value.lstrip('-')

    return sanitized_value


#typeconversion
def convert_string_integer(s):
    s = s.strip()
    if not s:
        return "0.0"
    if s.endswith('-'):
        s = '-' + ''.join(i for i in s[:-1] if i != ',')
    else:
        s = ''.join(i for i in s if i != ',')
    k=clean_value(s)
    return k




with open(file_path, 'r') as file:
    content = file.read()

split_files=content.split('\f')
flat_list=[]

for rows in split_files:
    flat_list.append(rows.split('\n\n\n'))

incomplete_trade=[]
merged_trade=''

# to extract details of body
def extract_values(record):
    global merged_trade
    global incomplete_trade
    trade_set_values = []
    summary_values = []
    global date
    global account


    for rec in record[0:1]:
        date=rec[94:102].strip()
        date = pd.to_datetime(date, format="%m/%d/%y")
        account=rec[168:178].strip()


    for idx, row_val in enumerate(record[1:]):

        each_rec = row_val.split("\n\n")



        for i,rec in enumerate(each_rec):

            if 'SECURITY' in each_rec[-1].split():


                if incomplete_trade:
                    each_rec = incomplete_trade+each_rec

                    incomplete_trade=[]

                for i in range(0,len(each_rec)-1):

                    trade_values={
                        "security_description": extract_security(each_rec[i]) if each_rec[i].split()[0].isalpha() else extract_security(each_rec[i-i])
                        if each_rec[i-i].split()[0].isalpha() else extract_security(each_rec[0]),
                        "cu_sip": each_rec[-1][22:35].strip(),
                        "lot_quantity": int(convert_string_integer(each_rec[i][22:35].strip())),
                        "trade_date": pd.to_datetime(each_rec[i][36:45].strip()).date(),
                        "settlement_date":pd.to_datetime( extract_settlement_date(each_rec[i])).date(),
                        "execution_date": pd.to_datetime(each_rec[i][36:45].strip()).date(),
                        "ref_no": extract_ref_no(each_rec[i]),
                        "price": convert_string_integer(each_rec[i][55:64].strip()),
                        "open_amount":float(convert_string_integer(each_rec[i][65:79].strip())),
                        "current_price": float(convert_string_integer(each_rec[i][80:89].strip())),
                        "current_market_value": float(convert_string_integer(each_rec[i][90:105].strip())),
                        "unrealized_p_and_l":float(convert_string_integer(each_rec[i][106:119].strip())),
                        "trade_int": float(convert_string_integer(each_rec[i][120:131].strip())),
                        "accrued_int":float( convert_string_integer(extract_a_val(each_rec[i])))
                    }


                    trade_set_values.append(trade_values)


                if 'SECURITY' in each_rec[-1].split():

                    k=0
                    summary_accrued=extract_summary_accrued(each_rec[-1])


                summary_val=    {
                        "security_description":
                             each_rec[-1][0:20] .strip(),

                        "cu_sip": each_rec[-1][22:35],


                        "lot_quantity": ''.join(i for i in each_rec[-1].split('\n')[1]

                        [22:35].strip() if i != ','),
                        "open_amount": float(convert_string_integer(each_rec[-1].split('\n')[1][65:79].strip())),

                        "current_market_value": float(convert_string_integer(each_rec[-1].split('\n')[1][
                            90:105
                        ].strip())),
                        "unrealized_p_and_l": float(convert_string_integer(each_rec[-2][
                            106:119
                        ].strip())),
                        "trade_int": float(convert_string_integer(each_rec[-1].split('\n')[1][
                            120:131
                        ].strip())),
                        "accrued_int":  float(convert_string_integer('-'+ summary_accrued[:-1]if summary_accrued.endswith('-') else summary_accrued))
                    }
                summary_values.append(summary_val)
                break

            else:
                incomplete_trade.append(each_rec[i])


    return trade_set_values,summary_values


def save_to_db(trade_set_values,summary_values, test_purpose = False, test_engine = None):
    trade_df=pd.DataFrame(trade_set_values)

    trade_df['For']=date
    trade_df['account']= account.replace("-","")

    summary_df = pd.DataFrame(summary_values)
    summary_df['For']=date
    summary_df['account']= account.replace("-","")

    trade_df = trade_df.rename(columns={"For":"for_date"})
    summary_df = summary_df.rename(columns={"For":"for_date"})

    trade_df['lot_quantity'] = pd.to_numeric(trade_df['lot_quantity'], errors='coerce')
    summary_df['lot_quantity'] = pd.to_numeric(summary_df['lot_quantity'], errors='coerce')

    dialect_and_driver='mysql+pymysql:'
    username = "root"
    password = "61945"
    hostname = "localhost"
    port = 3306
    db_name = "stock_details"

    url = f"{dialect_and_driver}//{username}:{password}@{hostname}:{port}/{db_name}"
    engine = create_engine(url)

    if test_purpose:
        #url = "sqlite:///file::memory:?cache=shared"
        engine = test_engine



    with engine.connect() as connection:
        # creating trade_details table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS trade_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
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
                id INT AUTO_INCREMENT PRIMARY KEY,
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

        # inserting trade details to trade table
        trade_df.to_sql(con=engine, name="trade_details", if_exists="append", index=False, chunksize=100)
        print("Trade Details inserted successfully.")

        # inserting summary details to summary table
        summary_df.to_sql(con=engine, name="summary_details", if_exists="append", index=False, chunksize=100)
        print("Summary Details inserted successfully.")

        connection.commit()



def process_all_records(flat_list, testing = False, **kwargs):
    trade_set_values = []
    summary_values = []


    for record in flat_list:
        trade_data, summary_data = extract_values(record)
        trade_set_values.extend(trade_data)
        summary_values.extend(summary_data)

    test_engine = kwargs.get("engine")

    save_to_db(trade_set_values, summary_values, test_purpose = testing, test_engine = test_engine)
    return 'summary and trade created'


start=time.time()
if __name__ == "__main__":
    process_all_records(flat_list)


end=time.time()
print('Time taken to parse the file:',end-start)



















