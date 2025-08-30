from database import engine, Base
import sys
import traceback

try:
    Base.metadata.create_all(bind=engine)
    print('Table creation successful')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc(file=sys.stdout)
