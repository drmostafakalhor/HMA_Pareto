
num_repeats = 1


for _ in range(num_repeats):      
    import numpy as np
    import random
    from tabulate import tabulate

    
    bitumen_range = (11, 60)
    RAP_range = (0, 500)
    lime_range = (2.5, 3.5)


    
    bitumen_cost_range = (0.404, 0.498)
    sand_gravel_cost_range = (0.011, 0.025)
    lime_cost = 0.120  
    transport_cost_range = (0.00043, 0.00176)
    rap_cost = (0.00043,0.00176)  
    electricity_cost_range = (0.4 * 0.95, 0.4 * 1.05)
    electricity_consumption = 5.2  

    
    transport_distance = (50, 200)

    
    fuel_costs = {
        "Lignite": (0.107,0.15),
        "Coal": (0.09725*0.8, 0.09725*0.12),
        "Oil": (0.538*0.8, 0.538*1.2),
        "Green Hydrogen": (3, 8),
        "Natural Gas": (0.42,0.573)
    }
    fuel_types = list(fuel_costs.keys())

    
    fuel_GWP = {
        "Lignite": 0.207,
        "Coal": 0.206,
        "Oil": 0.097,
        "Green Hydrogen": 0.0,
        "Natural Gas": 0.0817
    }

    
    heat_capacity = {"bitumen": 2000, "sand_gravel": 900, "RAP": 900, "lime": 850}

    fuel_heat_capacity = {
        "Lignite": (10,18),
        "Coal": (17.4,23.9)   ,       
        "Oil": (42,45)  ,  
        "Green Hydrogen": (120,140)  ,
        "Natural Gas": (42,55)    ,
    }

    
    initial_temp_range = (5, 17)

    
    def generate_asphalt_combinations(num_combinations):
        combinations = []
        
        for _ in range(num_combinations):
            bitumen = np.random.uniform(*bitumen_range) / 1000
            RAP = np.random.uniform(*RAP_range) / 1000
            lime = np.random.uniform(*lime_range) / 1000
            
            
            sand = (149 - 0.156 * (RAP * 1000)) / 1000
            gravel = (805 - 0.842 * (RAP * 1000)) / 1000
            bit_RAP = (0.064 * (RAP * 1000)) / 1000

            current_mix = {
                "sand": sand,
                "gravel": gravel,
                "lime": lime,
                "bitumen": bitumen,
                "RAP": RAP,
                "bit_RAP": bit_RAP
            }

           

            if RAP== 0:
                quality = 1  
            else:
        
                quality = max(0.5, 1 - (1000*RAP / 500) * 0.5)  
                     
              
               
            
            initial_temp = np.random.uniform(*initial_temp_range)
            target_temp = np.random.uniform(170, 180)
            
            
            total_heat_capacity = (
                bitumen*1000 * heat_capacity["bitumen"] +
                sand*1000 * heat_capacity["sand_gravel"] +
                gravel*1000 * heat_capacity["sand_gravel"] +
                RAP *1000* heat_capacity["RAP"] +
                lime*1000 * heat_capacity["lime"]
            )

            
            total_heat_capacity_MJ = total_heat_capacity/1000000

            
            heat_required = total_heat_capacity_MJ * (target_temp - initial_temp)  

            

            def get_fuel_combination(heat_required, fuel_types, fuel_heat_capacity):
                num_fuels = random.randint(1, 5)  
                fuel_mix = random.choices(fuel_types, k=num_fuels)

                fuel_ratio = np.random.dirichlet(np.ones(num_fuels), size=1)[0]

                fuel_consumption = {}
                for fuel, ratio in zip(fuel_mix, fuel_ratio):
                    fuel_energy = np.random.uniform(*fuel_heat_capacity[fuel])  # 
                    fuel_consumption[fuel] = ratio * heat_required / fuel_energy  

                total_energy_provided = sum(fuel_consumption[fuel] * np.random.uniform(*fuel_heat_capacity[fuel]) for fuel in fuel_consumption)

                max_iterations = 1000000  
                tolerance = 10  

                for _ in range(max_iterations):
                    if abs(total_energy_provided - heat_required) < tolerance:
                        return fuel_consumption

                    fuel_ratio = np.random.dirichlet(np.ones(num_fuels), size=1)[0]
                    fuel_consumption = {}
                    for fuel, ratio in zip(fuel_mix, fuel_ratio):
                        fuel_energy = np.random.uniform(*fuel_heat_capacity[fuel])  # 
                        fuel_consumption[fuel] = ratio * heat_required / fuel_energy  

                    total_energy_provided = sum(fuel_consumption[fuel] * np.random.uniform(*fuel_heat_capacity[fuel]) for fuel in fuel_consumption)

                raise ValueError("Fuel combinations could not provide the required energy.")
            
            
            fuel_consumption = get_fuel_combination(heat_required, fuel_types, fuel_heat_capacity)

            

    
            bitumen_cost = bitumen * np.random.uniform(*bitumen_cost_range)
            sand_cost = sand * np.random.uniform(*sand_gravel_cost_range)
            gravel_cost = gravel * np.random.uniform(*sand_gravel_cost_range)
            rap_cost_total = RAP * np.random.uniform(*rap_cost)
            lime_cost_total = lime * lime_cost
            transport_cost = np.random.uniform(*transport_cost_range) * np.random.uniform(*transport_distance)
            electricity_cost_total = np.random.uniform(*electricity_cost_range) * electricity_consumption

            
            LCC = (
                bitumen_cost
                + sand_cost
                + gravel_cost
                + rap_cost_total
                + lime_cost_total
                + transport_cost
                + electricity_cost_total
            )


                  
            fuel_cost_total = 0
            for fuel, consumption in fuel_consumption.items():
                
                fuel_cost_total += consumption * np.random.uniform(*fuel_costs[fuel])
            
            LCC += fuel_cost_total

             
            fuel_transport_cost_total = 0
            for fuel, consumption in fuel_consumption.items():
                
                fuel_transport_cost_total += consumption * np.random.uniform(*transport_distance)*np.random.uniform(*transport_cost_range)
            
            LCC += fuel_transport_cost_total

            
            transport_GWP = 0
            transport_GWP += (np.random.uniform(*transport_distance) * 0.0827)

            
            total_fuel_GWP = 0
            for fuel, amount in fuel_consumption.items():
                energy_consumed = amount * np.random.uniform(*fuel_heat_capacity[fuel] ) 
                total_fuel_GWP += (fuel_GWP[fuel] * energy_consumed)  

            
            GWP = total_fuel_GWP + transport_GWP + (bitumen * 340) + (sand * 1000 * 0.00205) + (gravel * 1000 * 0.00204) + (lime * 1000 * 0.00466)

           
            
            combinations.append([LCC, GWP, quality, bitumen * 1000, RAP * 1000, lime * 1000, sand * 1000, gravel * 1000, bit_RAP * 1000,
                                 fuel_consumption, sum(fuel_consumption.values()), target_temp])

        return combinations

    
    num_combinations = 1
    combinations = generate_asphalt_combinations(num_combinations)

    
    headers = ["LCC", "GWP", "Quality", "Bitumen (kg)", "RAP (kg)", "Lime (kg)", "Sand (kg)", "Gravel (kg)", "Bit_RAP (kg)", "Fuel Consumption (kg)", "Total Fuel Required (kg)"]

    
    
 
    output_data = []
    for row in combinations:
                # **
                fuel_consumption_str = ", ".join([f"{fuel}: {amount:.2f} kg" for fuel, amount in row[9].items()])
                
                # **
                output_data.append(row[:9] + [fuel_consumption_str, row[10], row[11]])  

            # **
    clean_output_data = []
    for row in output_data:
                clean_row = []
                for x in row:
                    # ****
                    if isinstance(x, np.ndarray):
                        clean_row.append(x.tolist())
                    elif isinstance(x, np.float64):
                        clean_row.append(float(x))
                    else:
                        clean_row.append(x)
                clean_output_data.append(clean_row)

            # ***
    print(tabulate(clean_output_data, headers=headers, tablefmt="grid"))




    import pandas as pd

    
    df = pd.DataFrame(combinations, columns=["LCC", "GWP", "Quality", "Bitumen (kg)", "RAP (kg)", "Lime (kg)", "Sand (kg)", "Gravel (kg)", "Bit_RAP (kg)", "Fuel Consumption (kg)", "Total Fuel Required (kg)", "Target Temperature (°C)"])

    
    df.to_csv('asphalt_combinations.csv', index=False)


    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    
    df = pd.read_csv("asphalt_combinations.csv")

    
    required_columns = ['LCC', 'GWP', 'Quality', 'Bitumen (kg)', 'RAP (kg)', 'Lime (kg)', 'Sand (kg)', 'Gravel (kg)', 'Bit_RAP (kg)', 'Fuel Consumption (kg)', 'Total Fuel Required (kg)', 'Target Temperature (°C)']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in the CSV file!")

    
    data = df[required_columns[:3]].values  

    
    def is_pareto_efficient(costs):
        is_efficient = np.ones(costs.shape[0], dtype=bool)
        for i, c in enumerate(costs):
            if is_efficient[i]:
                is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)
                is_efficient[i] = True
        return is_efficient

    
    pareto_mask = is_pareto_efficient(data)

    
    pareto_df = df[pareto_mask]
    
    import os

    pareto_file = "pareto_optimal.csv"

    # 
    if os.path.exists(pareto_file):
        existing_pareto_df = pd.read_csv(pareto_file)
        pareto_df = pd.concat([existing_pareto_df, pareto_df], ignore_index=True)

    pareto_df.to_csv(pareto_file, index=False)
    print("All Pareto combinations saved in 'pareto_optimal.csv'.")

    print("Optimal results saved in 'pareto_optimal.csv'.")


    import pandas as pd

    
    pareto_df = pd.read_csv("pareto_optimal.csv")

    
    fuel_statistics = {
        "Lignite": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Coal": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Oil": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Green Hydrogen": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Natural Gas": {"count": 0, "total_kg": 0, "total_MJ": 0}
    }

    
    fuel_heat_capacity = {
        "Lignite": 24,  
        "Coal": 25,     
        "Oil": 42,      
        "Green Hydrogen": 120,  
        "Natural Gas": 50  
    }

    for index, row in pareto_df.iterrows():
        fuel_consumption = eval(row['Fuel Consumption (kg)'])  # 

    for fuel, amount in fuel_consumption.items():
        if fuel in fuel_statistics:
            fuel_statistics[fuel]["count"] += 1  # 
            fuel_statistics[fuel]["total_kg"] += amount  #
            fuel_statistics[fuel]["total_MJ"] += amount * fuel_heat_capacity[fuel]  # 

    
    for fuel, stats in fuel_statistics.items():
        print(f"{fuel}: {stats['count']} occurrences, {stats['total_kg']:.2f} kg, {stats['total_MJ']:.2f} MJ")

    import pandas as pd

    
    n = num_repeats  



    
    fuel_statistics = {
        "Lignite": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Coal": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Oil": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Green Hydrogen": {"count": 0, "total_kg": 0, "total_MJ": 0},
        "Natural Gas": {"count": 0, "total_kg": 0, "total_MJ": 0}
    }

    
    fuel_heat_capacity = {
        "Lignite": 24,  
        "Coal": 25,     
        "Oil": 42,      
        "Green Hydrogen": 120,  
        "Natural Gas": 50  
    }

    
    for i in range(n):  
        
        pareto_df = pd.read_csv("pareto_optimal.csv")

        
        for index, row in pareto_df.iterrows():
            fuel_consumption = eval(row['Fuel Consumption (kg)'])  
            
            
            for fuel, amount in fuel_consumption.items():
                if fuel in fuel_statistics:
                    fuel_statistics[fuel]["count"] += 1
                    fuel_statistics[fuel]["total_kg"] += amount
                    fuel_statistics[fuel]["total_MJ"] += amount * fuel_heat_capacity[fuel]

    
    all_results = []
    for fuel, stats in fuel_statistics.items():
        all_results.append({
            "Fuel": fuel,
            "Count": stats["count"],
            "Total kg": stats["total_kg"],
            "Total MJ": stats["total_MJ"]
        })

    
    fuel_stats_df = pd.DataFrame(all_results)

    
    fuel_stats_df.to_excel("fuel_statistics.xlsx", index=False, sheet_name="Fuel Stats")

    print("All aggregated data has been saved in fuel_statistics.xlsx.")



