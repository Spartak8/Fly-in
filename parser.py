class Parser:
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        nb_drones = 0
        graph = Graph()
        with open(self.filename) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("nb_drones"):
                    amount = line.strip().split()
                    if len(amount) != 2:
                        raise ValueError("Invalid nb_drones line")
                    try:
                        nb_drones = int(amount[1])
                    except ValueError:
                        raise ValueError("nb_drones must be an integer")
                    if nb_drones <= 0:
                        raise ValueError("nb_drones must be a positive integer")
                elif line.startswith("start_hub"):
                    pass
                elif line.startswith("end_hub"):
                    pass
                elif line.startswith("hub"):
                    pass
                elif line.startswith("connection"):
                    pass



                
                    

