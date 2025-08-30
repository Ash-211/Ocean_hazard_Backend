from database import engine
import sqlalchemy as sa

with engine.connect() as conn:
    result = conn.execute(sa.text('SELECT email, role, is_active, is_verified FROM users'))
    for row in result:
        print(f'Email: {row[0]}, Role: {row[1]}, Active: {row[2]}, Verified: {row[3]}')
