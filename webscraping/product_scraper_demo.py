from product_scraper import ProductScraper
from product_scraper import FlowerCategory
#Need to run pip install PuLP, which is ok, but we need to figure out how this can be done automatically on Paula's computer - Use subprocesses to call pip
#https://sqlpey.com/python/solved-how-to-install-a-python-module-within-code/
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value

scraper = ProductScraper()
result = scraper.scrape_products(FlowerCategory.CARNATION)

print(result)

datalist = result
   

requested_flower_type = input("Please enter your desired flower: Ex: 'Rose', 'Lily', or 'Sunflower': ").capitalize()
stem_length_low = int(input("Please enter the lower range of allowable stem length (cm): "))
stem_length_high = int(input("Please enter the upper range of allowable stem length (cm): "))
amount_low = int(input("Please enter the lower range of total number of flowers you need: "))
amount_high = int(input("Please enter the upper range of total number of flowers you need: "))
season = input("Please enter the season/event: (Fall: 'F', Spring: 'Sp', Winter: 'W', Summer: 'Su':, Mothers Day: 'Md', Valentines Day: 'Vd', Funeral: 'F'): ") #Also include event as season ex. mothers day, funeral, valentines day
color = input("Please enter desired color. Ex: Red, Blue, White: ").capitalize()


print("----------------------------------------------------------------------------------------------------")
#Substitutions for requested flower type based on type and color of flower
flower_subs = {
    'Rose': {
        'Red': ['Alstro', 'Poms', 'Carnation'],
        'Blue': ['Alstro', 'Poms', 'Carnation'],
        'Pink': ['Lily', 'Alstro', 'Poms', 'Carnation'],
        'White': ['Lily', 'Alstro', 'Poms', 'Carnation'],
        'Purple': ['Alstro', 'Poms', 'Carnation'],
        'Orange': ['Lily', 'Alstro', 'Poms', 'Carnation'],
        'Yellow': ['Lily', 'Alstro', 'Poms', 'Carnation']
    },
    'Tulip': {
        'Red': [],
        'Blue': [],
        'Pink': [],
        'White': [],
        'Purple': [],
        'Orange': [],
        'Yellow': []
    },
    'Sunflower': {
        'Red': ['Rose'],
        'Blue': [],
        'Pink': ['Rose'],
        'White': ['Rose', 'Hydrangea'],
        'Purple': ['Poms', 'Daisy', 'Carnation'],
        'Orange': ['Rose'],
        'Yellow': ['Rose']
    },
    'Lily': {
        'Red': ['Poms', 'Daisy', 'Carnation'],
        'Blue': ['Poms', 'Daisy', 'Carnation'],
        'Pink': ['Poms', 'Daisy', 'Carnation'],
        'White': ['Poms', 'Daisy', 'Carnation'],
        'Purple': ['Poms', 'Daisy', 'Carnation'],
        'Orange': ['Poms', 'Daisy', 'Carnation'],
        'Yellow': ['Poms', 'Daisy', 'Carnation']
    },
    'Alstro': {
        'Red': ['Poms', 'Daisy', 'Carnation'],
        'Blue': ['Poms', 'Daisy', 'Carnation'],
        'Pink': ['Poms', 'Daisy', 'Carnation'],
        'White': ['Poms', 'Daisy', 'Carnation'],
        'Purple': ['Poms', 'Daisy', 'Carnation'],
        'Orange': ['Poms', 'Daisy', 'Carnation'],
        'Yellow': ['Poms', 'Daisy', 'Carnation']
    },
    'Poms': {
        'Red': ['Alstro', 'Daisy', 'Carnation'],
        'Blue': ['Alstro', 'Daisy', 'Carnation'],
        'Pink': ['Alstro', 'Daisy', 'Carnation'],
        'White': ['Alstro', 'Daisy', 'Carnation'],
        'Purple': ['Alstro', 'Daisy', 'Carnation'],
        'Orange': ['Alstro', 'Daisy', 'Carnation'],
        'Yellow': ['Alstro', 'Daisy', 'Carnation']
    },
    'Daisy': {
        'Red': ['Alstro', 'Poms', 'Carnation'],
        'Blue': ['Alstro', 'Poms', 'Carnation'],
        'Pink': ['Alstro', 'Poms', 'Carnation'],
        'White': ['Alstro', 'Poms', 'Carnation'],
        'Purple': ['Alstro', 'Poms', 'Carnation'],
        'Orange': ['Alstro', 'Poms', 'Carnation'],
        'Yellow': ['Alstro', 'Poms', 'Carnation']
    },
    'Carnation': {
        'Red': ['Alstro', 'Poms', 'Daisy'],
        'Blue': ['Alstro', 'Poms', 'Daisy'],
        'Pink': ['Alstro', 'Poms', 'Daisy'],
        'White': ['Alstro', 'Poms', 'Daisy'],
        'Purple': ['Alstro', 'Poms', 'Daisy'],
        'Orange': ['Alstro', 'Poms', 'Daisy'],
        'Yellow': ['Alstro', 'Poms', 'Daisy']
    },
    'Hydrangea': {
        'Red': [],
        'Blue': ['Rose', 'Lily', 'Carnation'],
        'Pink': [],
        'White': ['Rose', 'Lily', 'Carnation'],
        'Purple': ['Rose', 'Lily', 'Carnation'],
        'Orange': [],
        'Yellow': []
    }
}
filteredlist = []   
#This for loop filters out: Flowers that aren't the requested type or an acceptable substitute, Flowers with a color that is not the requested color,
#Flowers with a stem length outside the allowable range, and Flowers that won't get shipped within 48 hours                                                                         
for flower in datalist:
    if (
        (flower["Type"] == requested_flower_type or flower["Type"] in flower_subs.get(requested_flower_type).get(color))
        and (flower["Color"] == color)
        and (stem_length_low <= flower["Stem Length"] <= stem_length_high)
        and (flower["Shipping Time (Hours)"] <= 48)
    ):
        filteredlist.append(flower)




#---------------------Replaced Gurobi with pulp -------------------------

model = LpProblem("Maximize_Example", LpMinimize)#<-we made a model called "model."
#x represents the number of packages of each flower we want to order. It is set to an integer; the value of this variable needs to represent a discrete number of packages
x = {flower["Identifier"]: LpVariable(name=f"x_{flower['Identifier']}",lowBound=0,cat="Integer")for flower in filteredlist}
#adding constraints...the total number of flowers for whatever combination of flowers we select has to be greater than amount low and less than amount high.
model += ((lpSum((x[flower["Identifier"]] * flower["Number of Flowers per Package"]) for flower in filteredlist)) <= amount_high), "Constraint 1" 
model += ((lpSum((x[flower["Identifier"]] * flower["Number of Flowers per Package"]) for flower in filteredlist)) >= amount_low), "Constraint 2"
#We want to minimize the total cost of our order! So, minimize the sum over all flowers of the flowers' cost times the number of each flower we buy
objective_expression = (lpSum((x[flower["Identifier"]] * flower["Cost"]) for flower in filteredlist))
model += objective_expression, "Objective"


num_solutions = 5 #Adjust this number to change the number of options the user has to pick from
solutions = []  # List to store all optimal solutions found
previous__solution = -float("inf")  # Initialize with negative infinity to minimize cost of first solution

# Generate multiple optimal solutions by iteratively adding constraints
for i in range(1,num_solutions+1):
    # For solutions after the first, add constraint to find a worse solution than the previous one
    if i> 1:
        model += objective_expression >= previous__solution +0.001, f"New Objective {i}"
    model.solve()
    
    # Check if an optimal solution was found
    if LpStatus[model.status] == "Optimal":
        # Extract the objective value (total cost) from the current solution
        current_cost = value(model.objective)
        current_solution = {'Cost': current_cost, 'Order': [], 'TotalFlowers': 0}
        
        # Iterate through all decision variables to build the order details
        for identifier, var in x.items():
            # Get the number of packages for this flower identifier
            if var.varValue is not None:
                packages = int(var.varValue)  
            else:
                packages = 0

            if packages > 0:
                # Find the package size to calculate total flowers
                flower_data = next(f for f in filteredlist if f["Identifier"] == identifier)
                current_solution['Order'].append(f"{packages} packages of {identifier}")
                current_solution['TotalFlowers'] += packages * flower_data["Number of Flowers per Package"]
        
        # Add the current solution to the list and update the previous solution cost
        solutions.append(current_solution)
        previous__solution = current_cost
    else:
        # No more optimal solutions can be found
        print("Maximum number of solutions generated.")
        break

print("-"*20)
print("Your optimal order is: ")

#1 means there was a procurement option that fits whatever constraints Paula wants, while -1 or -2 means that there isn't
if solutions == []:
    print(f"No solution found that meets all constraints.")
else:
    for i, solution in enumerate(solutions):
        print(f"#{i+1} BEST SOLUTION")
        print(f"Total Cost: ${solution['Cost']:.2f}")
        print("Order Details:")
        
        if solution['Order'] != []:
            for line in solution['Order']:
                print(f" {line}")
        print(f"Total Flowers Procured: {int(solution['TotalFlowers'])}")
        print("-" * 20)


del model
