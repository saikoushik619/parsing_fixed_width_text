Requirements
-
    -Mysql
    -Sqlalchemy
    -Pandas
Packages Required
-
    -pip install sqlalchemy
Modules Required
-
    -install create_engine,tet from sql alchemy
    -install pandas 
Approach followed
-
    -classic slicing Aproach.
    -Intially split the file by formfeed ('\f') to get separate individual pages from file.
    -Next step split the individual page by newline('\n') to get individual set of records.
    -Separate the header and body part to get body values and header values separately.
    - As file is a machine generated it occupies fixed width column size based on that width 
      we extract the data according to the column size(#field name width).
    - convert the extracted data to a dataframe using pandas .
    - Use sqlAlchemy to create engine with the mysql database credentials.
    -Insert the parsed data to database and validate it.

    
    
Problem
-
    -Parse a fixed width text file using classic slicing approach using python and store it in the database.
Business
-
    -Parse a fixed width text file and store it in the database.
Solution
-
    -Split the file by formFeed('\f) to get separate individual page from file.
    -Next step split the individual page by newline('\n') to get individual set of records.
    -check whether record is trade set or summary set based on the 'security' word present or not in record.
    -Extract the data based on the column width and assign it to the variable according to the column name.
    -Append to the list for every completion of record and convert it to the dataframe.
    -Follow the same process for summary record set.

