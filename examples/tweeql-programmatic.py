from tweeql.exceptions import TweeQLException
from tweeql.query_runner import QueryRunner

runner = QueryRunner()
runner.run_query("SELECT text FROM twitter_sample;", False)
#runner.stop_query()
