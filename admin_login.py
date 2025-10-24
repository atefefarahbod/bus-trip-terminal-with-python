import argparse
from authentication import Authentication

class AdminLogin:
    def __init__(self):
        self.auth = Authentication()
    
    def setup_parser(self):
        parser = argparse.ArgumentParser(description='admin entrance')
        parser.add_argument('--username', required=True, help='admin username')
        parser.add_argument('--password', required=True, help='admin password')
        return parser
    
    def run(self):
        parser = self.setup_parser()
        args = parser.parse_args()
        
        if self.auth.is_superuser(args.username, args.password):
            print(f"{args.username} entered")
        else:
            print("error")

if __name__ == "__main__":
    admin = AdminLogin()
    admin.run()