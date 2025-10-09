from cli import CLI

def test_cli():
     
    cli = CLI()
    print("1. test fot cli")
    if cli.authentication:
        print("created auth")
    else:
        print("error")
    
    
    print("2. test first current user")
    if cli.authentication.current_user is None:
        print("current_user correct")
    else:
        print("current_user false")
    
    
if __name__ == "__main__":
    test_cli()