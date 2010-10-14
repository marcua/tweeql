from tweeql.exceptions import TweeQLException
from tweeql.field_descriptor import ReturnType
from tweeql.function_registry import FunctionInformation, FunctionRegistry
from tweeql.query_runner import QueryRunner

class StringLength():
    return_type = ReturnType.INTEGER

    @staticmethod
    def factory():
        return StringLength().strlen

    def strlen(self, tuple_data, val):
        """ 
            Returns the length of val, which is a string
        """
        return len(val)

fr = FunctionRegistry()
fr.register("stringlength", FunctionInformation(StringLength.factory, StringLength.return_type))

runner = QueryRunner()
runner.run_query("SELECT stringlength(text) AS len FROM twitter_sample;", False)
