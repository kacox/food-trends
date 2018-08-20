"""Make engine at module level.

From the docs:
'The typical usage of create_engine() is once per particular database URL, 
held globally for the lifetime of a single application process. A single 
Engine manages many individual DBAPI connections on behalf of the process and 
is intended to be called upon in a concurrent fashion. The Engine is not 
synonymous to the DBAPI connect function, which represents just one connection 
resource - the Engine is most efficient when created just once at the module 
level of an application, not per-object or per-function call.'
"""

from sqlalchemy import create_engine

engine = create_engine("postgresql:///food_trends", echo=False)