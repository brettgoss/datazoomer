"""
    sqltools.py
    experimental!

    note: currently designed to work with mysql and cousins only
"""

import itertools

__all__ = ['summarize']

def setup_tst():
    def create_test_tables(db):
        db("""
        create table if not exists person (
            id int not null auto_increment,
            name      varchar(100),
            age       smallint,
            kids      smallint,
            salary    decimal(10,2),
            birthdate date,
            PRIMARY KEY (id)
            )
        """)
    
    def delete_test_tables(db):
        db('drop table if exists person')

    import MySQLdb, db

    db = db.Database(
            MySQLdb.Connect, 
            host='database',
            db='test',
            user='testuser',
            passwd='password')
    db.autocommit(1)
    delete_test_tables(db)
    create_test_tables(db)
    return db

def summarize(table, dimensions, metrics=[]):
    """
    summarize a table

    >>> from records import Record, RecordStore
    >>> from decimal import Decimal
    >>> db = setup_tst()
    >>> class Person(Record): pass
    >>> class People(RecordStore): pass
    >>> people = People(db, Person)
    >>> id = people.put(Person(name='Sam', age=25, kids=1, salary=Decimal('40000')))
    >>> id = people.put(Person(name='Sally', age=55, kids=4, salary=Decimal('80000')))
    >>> id = people.put(Person(name='Bob', age=25, kids=2, salary=Decimal('70000')))
    >>> id = people.put(Person(name='Jane', age=25, kids=2, salary=Decimal('50000')))
    >>> id = people.put(Person(name='Alex', age=25, kids=3, salary=Decimal('50000')))
    >>> print people
    person
        id  kids  age  name   salary    
    ------- ----- ---- ------ --------- 
         1  1     25   Sam    40000.00  
         2  4     55   Sally  80000.00  
         3  2     25   Bob    70000.00  
         4  2     25   Jane   50000.00  
         5  3     25   Alex   50000.00  
    5 records
    >>> print db(summarize('person', ['age']))
      age   n 
     ----- ---
      *     5 
      25    4 
      55    1 
    >>> print db(summarize('person', ['age','kids']))
      age   kids   n 
     ----- ------ ---
      *     *      5 
      *     1      1 
      *     2      2 
      *     3      1 
      *     4      1 
      25    *      4 
      55    *      1 
      25    1      1 
      25    2      2 
      25    3      1 
      55    4      1 
    >>> print db(summarize('person', ['age','kids'], ['salary']))
      age   kids   n      salary 
     ----- ------ --- -----------
      *     *      5   290000.00 
      *     1      1    40000.00 
      *     2      2   120000.00 
      *     3      1    50000.00 
      *     4      1    80000.00 
      25    *      4   210000.00 
      55    *      1    80000.00 
      25    1      1    40000.00 
      25    2      2   120000.00 
      25    3      1    50000.00 
      55    4      1    80000.00 
    >>> people.zap()
    >>> print people
    Empty list
    """

    statement_tpl = 'select {dims}, {calcs} from {table} group by {cols}'
    d = [i.split()[:1][0] for i in dimensions]
    c = [i.split()[-1:][0] for i in dimensions]
    lst = []

    for s in list(itertools.product([0,1], repeat=len(dimensions))):
        dims = ', '.join([s[i] and d[i] + ' '+ c[i] or '"*" ' + c[i] for i,_ in enumerate(s)])
        calcs = ', '.join(['count(*) n'] + ['sum({}) {}'.format(m,m) for m in metrics])
        cols = ', '.join([str(n+1) for n,_ in enumerate(c)])
        lst.append(statement_tpl.format(**locals()))

    cmd = '\nunion '.join(lst)
    return cmd
    #return db(cmd)

#if __name__ == '__main__':
#    import doctest
#    doctest.testmod()


