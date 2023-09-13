from Bake import target, bake


@target
def my_under_function_9():
    """doc string for my under function"""
    print("Underbars are standard!")

@target
def my_Under_Function_9():
    """doc string for my under function"""
    print("Underbars are standard!")


@target
def myCamelFunction9():
    """doc string for myCamelFunction"""
    print("CamelsAreStellar!")


if __name__ == "__main__":
    bake()
