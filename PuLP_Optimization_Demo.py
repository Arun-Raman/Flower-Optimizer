#Need to run pip install gurobipy, which is ok, but we need to figure out how this can be done automatically on Paula's computer
from pulp import LpProblem, LpVariable, LpMinimize, lpSum
#I kept this really simple. We'll definitely have some flower bundles that might have some amount of different colors and flowers, so we'd need to sort out what that looks like
#We just have to make sure that the datalist (shown below) returned by the web scraping team is what we need it to be. Or we might need to turn strings into integers, etc.
datalist = [
    {"Identifier": "Farm 1 Rose A", "Cost": 23.50, "Type": "Rose", "Color": "Yellow", "Number of Flowers per Package": 47, "Stem Length": 64, "Shipping Time (Hours)": 2},
    {"Identifier": "Farm 1 Rose B", "Cost": 11.50, "Type": "Rose", "Color": "Blue", "Number of Flowers per Package": 23, "Stem Length": 48, "Shipping Time (Hours)": 23},
    {"Identifier": "Farm 1 Lily A", "Cost": 33.00, "Type": "Lily", "Color": "Red", "Number of Flowers per Package": 32, "Stem Length": 48, "Shipping Time (Hours)": 23},
    {"Identifier": "Farm 2 Rose C", "Cost": 8.60, "Type": "Rose", "Color": "Red", "Number of Flowers per Package": 56, "Stem Length": 77, "Shipping Time (Hours)": 15},
    {"Identifier": "Farm 2 Rose D", "Cost": 14.43, "Type": "Rose", "Color": "Yellow", "Number of Flowers per Package": 89, "Stem Length": 63, "Shipping Time (Hours)": 58},
    {"Identifier": "Farm 3 Rose E", "Cost": 23.50, "Type": "Rose", "Color": "Blue", "Number of Flowers per Package": 41, "Stem Length": 58, "Shipping Time (Hours)": 9},
    {"Identifier": "Farm 3 Rose F", "Cost": 14.00, "Type": "Rose", "Color": "Red", "Number of Flowers per Package": 77, "Stem Length": 82, "Shipping Time (Hours)": 20},
    {"Identifier": "Farm 5 Rose I", "Cost": 9.50, "Type": "Rose", "Color": "White", "Number of Flowers per Package": 93, "Stem Length": 80, "Shipping Time (Hours)": 8},
    {"Identifier": "Farm 5 Rose J", "Cost": 23.50, "Type": "Rose", "Color": "Yellow", "Number of Flowers per Package": 46, "Stem Length": 68, "Shipping Time (Hours)": 39},
    {"Identifier": "Farm 6 Rose K", "Cost": 21.50, "Type": "Rose", "Color": "Red", "Number of Flowers per Package": 59, "Stem Length": 54, "Shipping Time (Hours)": 42},
    {"Identifier": "Farm 10 Daisy A", "Cost": 15.00, "Type": "Daisy", "Color": "Yellow", "Number of Flowers per Package": 67, "Stem Length": 49, "Shipping Time (Hours)": 40},
    {"Identifier": "Farm 10 Daisy B", "Cost": 27.50, "Type": "Daisy", "Color": "White", "Number of Flowers per Package": 21, "Stem Length": 57, "Shipping Time (Hours)": 27},
    {"Identifier": "Farm 6 Rose L", "Cost": 47.50, "Type": "Rose", "Color": "Pink", "Number of Flowers per Package": 22, "Stem Length": 60, "Shipping Time (Hours)": 16},
    {"Identifier": "Farm 7 Rose M", "Cost": 23.50, "Type": "Rose", "Color": "Red", "Number of Flowers per Package": 85, "Stem Length": 95, "Shipping Time (Hours)": 4},
    {"Identifier": "Farm 7 Rose N", "Cost": 23.50, "Type": "Rose", "Color": "Blue", "Number of Flowers per Package": 35, "Stem Length": 78, "Shipping Time (Hours)": 52},
    {"Identifier": "Farm 8 Tulip A", "Cost": 18.70, "Type": "Tulip", "Color": "Red", "Number of Flowers per Package": 54, "Stem Length": 70, "Shipping Time (Hours)": 25},
    {"Identifier": "Farm 8 Tulip B", "Cost": 23.50, "Type": "Tulip", "Color": "Yellow", "Number of Flowers per Package": 77, "Stem Length": 64, "Shipping Time (Hours)": 31},
    {"Identifier": "Farm 9 Lily B", "Cost": 23.50, "Type": "Lily", "Color": "White", "Number of Flowers per Package": 38, "Stem Length": 90, "Shipping Time (Hours)": 18},
    {"Identifier": "Farm 9 Lily C", "Cost": 20.90, "Type": "Lily", "Color": "Red", "Number of Flowers per Package": 44, "Stem Length": 66, "Shipping Time (Hours)": 12},
    {"Identifier": "Farm 11 Sunflower A", "Cost": 23.50, "Type": "Sunflower", "Color": "Yellow", "Number of Flowers per Package": 32, "Stem Length": 100, "Shipping Time (Hours)": 34},
    {"Identifier": "Farm 11 Sunflower B", "Cost": 23.50, "Type": "Sunflower", "Color": "Red", "Number of Flowers per Package": 60, "Stem Length": 85, "Shipping Time (Hours)": 10},
    {"Identifier": "Farm 12 Orchid A", "Cost": 23.50, "Type": "Orchid", "Color": "Purple", "Number of Flowers per Package": 27, "Stem Length": 48, "Shipping Time (Hours)": 37},
    {"Identifier": "Farm 12 Orchid B", "Cost": 20.50, "Type": "Orchid", "Color": "Yellow", "Number of Flowers per Package": 88, "Stem Length": 76, "Shipping Time (Hours)": 7},
    {"Identifier": "Farm 13 Carnation A", "Cost": 23.50, "Type": "Carnation", "Color": "Red", "Number of Flowers per Package": 49, "Stem Length": 61, "Shipping Time (Hours)": 14},
    {"Identifier": "Farm 13 Carnation B", "Cost": 13.50, "Type": "Carnation", "Color": "Pink", "Number of Flowers per Package": 25, "Stem Length": 46, "Shipping Time (Hours)": 55},
    {"Identifier": "Farm 14 Chrysanthemum A", "Cost": 43.30, "Type": "Chrysanthemum", "Color": "Yellow", "Number of Flowers per Package": 73, "Stem Length": 65, "Shipping Time (Hours)": 29},
    {"Identifier": "Farm 15 Tulip C", "Cost": 23.50, "Type": "Tulip", "Color": "Red", "Number of Flowers per Package": 58, "Stem Length": 84, "Shipping Time (Hours)": 50},
    {"Identifier": "Farm 15 Lily D", "Cost": 23.50, "Type": "Lily", "Color": "Yellow", "Number of Flowers per Package": 40, "Stem Length": 88, "Shipping Time (Hours)": 22},
    {"Identifier": "Farm 4 Rose G", "Cost": 13.50, "Type": "Rose", "Color": "Yellow", "Number of Flowers per Package": 52, "Stem Length": 75, "Shipping Time (Hours)": 11},
    {"Identifier": "Farm 4 Rose H", "Cost": 23.50, "Type": "Rose", "Color": "White", "Number of Flowers per Package": 64, "Stem Length": 71, "Shipping Time (Hours)": 33},
]

requested_flower_type = input("Please enter your desired flower: 'Rose', 'Lily', or 'Sunflower': ")
stem_length_low = int(input("Please enter the lower range of allowable stem length (cm): "))
stem_length_high = int(input("Please enter the upper range of allowable stem length (cm): "))
amount_low = int(input("Please enter the lower range of total number of flowers you need: "))
amount_high = int(input("Please enter the upper range of total number of flowers you need: "))
season = input("Please enter Fall: 'F', Spring: 'Sp', Winter: 'W', Summer: 'Su': ")
color = input("Please enter desired color (substitutions will vary by season), either red: 'R', blue: 'B', white: 'W': ")


print("----------------------------------------------------------------------------------------------------")

#This dictionary basically says: for each season, what colors can be substituted by what? I.E. In winter, because of valentine's day, a red maybe can be substituted with a pink, while in fall, a red maybe can be substituted by an orange (fall colors)
season_color_subs = {"F": {"R": ["Red", "Yellow", "White"], "B": ["Blue"], "W": ["White", "Yellow"]},
                     "W": {"R": ["Red", "Yellow", "Pink"], "B": ["Blue", "Green"], "W": ["White"]},
                     "Sp": {"R": ["Red", "Yellow"], "B": ["Blue", "Green"], "W": ["White"]},
                     "Su": {"R": ["Red", "Yellow"], "B": ["Blue", "Green"], "W": ["White"]},
                     }

filteredlist = []   
#This for loop filters out: Flowers that aren't the requested type, Flowers with a color that is NOT either the requested color or an acceptable substitute depending on the season,
#Flowers with a stem length outside the allowable range, and Flowers that won't get shipped within 48 hours                                                                         
for flower in datalist:
    if ((flower["Type"] == requested_flower_type) and (flower["Color"] in season_color_subs[season][color]) and (stem_length_low <= flower["Stem Length"] <= stem_length_high) and (flower["Shipping Time (Hours)"] <= 48)):
        filteredlist.append(flower)




#---------------------Replaced Gurobi with pulp -------------------------

model = LpProblem("Maximize_Example", LpMinimize)#<-we made a model called "model."
#x represents the number of packages of each flower we want to order. It is set to an integer; the value of this variable needs to represent a discrete number of packages
x = {flower["Identifier"]: LpVariable(name=f"x_{flower['Identifier']}",lowBound=0,cat="Integer")for flower in filteredlist}
#adding constraints...the total number of flowers for whatever combination of flowers we select has to be greater than amount low and less than amount high.
model += ((lpSum((x[flower["Identifier"]] * flower["Number of Flowers per Package"]) for flower in filteredlist)) <= amount_high), "Constraint 1" 
model += ((lpSum((x[flower["Identifier"]] * flower["Number of Flowers per Package"]) for flower in filteredlist)) >= amount_low), "Constraint 2"
#We want to minimize the total cost of our order! So, minimize the sum over all flowers of the flowers' cost times the number of each flower we buy
model += (lpSum((x[flower["Identifier"]] * flower["Cost"]) for flower in filteredlist)), "Objective"
model.solve() #update the model to take in all the changes

print("-----------------------------------------------------------------------------------------------------------------")
print("Your optimal order is: ")

#1 means there was a procurement option that fits whatever constraints Paula wants, while -1 or -2 means, for all intents and purposes, that there isn't
if (model.status == 1):
    for i in x:
        #For post-processing, pulp requires you to use the solution value, x[i].varValue, not just the variable at face value (like x[i])
        #We only want to print the flower identifier and the value of its associated variable (number of packages of that flower to order) if we actually want to order some nonzero amount of packages of that flower
        if (x[i].varValue != 0):
            print(f"{x[i].varValue} of {i}")
elif (model.status == -1 or model.status == -2):
    print("Model is either infeasible or unbounded.")

del model