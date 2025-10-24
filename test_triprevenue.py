from cli import CLI

def revenue_test():  
    
    cli = CLI()
    print("CLI created")
    
    if cli.authentication:
        print("Aut created")
    else:
        print("errorr in create aut")
        return
    
    if cli.authentication.current_user is None:
        print("current_user correct")
    else:
        print("current_user false")
    
    if cli.report_generator:
        print("ReportGenerator created ")
            
        try:
            revenue = cli.report_generator.get_trip_revenue(1)
            print(f"trip revenue: {revenue}")
        except Exception as e:
            print(f"errorr in revenue: {e}")
    else:
        print("ReportGenerator not created")

if __name__ == "__main__":
    revenue_test()