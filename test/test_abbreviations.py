from ..Bake import DefaultArgumentParser

class TestAbbreviations:

    parser = DefaultArgumentParser()

    def test_simple_method_names(self):
        assert self.parser.name_and_abbreviations(python_name="deploy") == ["deploy", "d"]
        assert self.parser.name_and_abbreviations(python_name="deploy_prod") == ["deploy_prod", "dp"]
        assert self.parser.name_and_abbreviations(python_name="deploy_prod_server_8") == ["deploy_prod_server_8", "dps8"]
        assert self.parser.name_and_abbreviations(python_name="deployProd") == ["deployProd", "dp"]
        assert self.parser.name_and_abbreviations(python_name="deployProd8") == ["deployProd8", "dp8"]
