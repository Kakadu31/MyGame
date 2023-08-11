import random

class flowfield:
    def __init__(self, width, height, cell_size, time_interval, fluctuation_strength):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.time_interval = time_interval
        self.num_cells_x = width // cell_size
        self.num_cells_y = height // cell_size
        self.grid = [[(0, 0) for _ in range(self.num_cells_x)] for _ in range(self.num_cells_y)]
        self.time_passed = 0
        self.fluctuation_strength = fluctuation_strength

    def set_flow_at(self, x, y, velocity):
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        self.grid[grid_y][grid_x] = velocity

    def get_flow_at(self, grid_x, grid_y):
        if 0 <= grid_x < self.num_cells_x and 0 <= grid_y < self.num_cells_y:
            return self.grid[grid_y][grid_x]
        return 0, 0
    
    def update(self, dt):
        self.time_passed += dt
        if self.time_passed >= self.time_interval:
            self.time_passed -= self.time_interval
            self.update_flowfield()
        # Adjust the flow vectors to create the illusion of currents
    def update_flowfield(self):
        for y in range(self.num_cells_y):
            for x in range(self.num_cells_x):
                # Gradually change the x and y components of the flow vector
                current_flow = self.grid[y][x]
                new_x = current_flow[0] + random.uniform(-self.fluctuation_strength, self.fluctuation_strength)
                new_y = current_flow[1] + random.uniform(-self.fluctuation_strength, self.fluctuation_strength)
                self.grid[y][x] = (new_x, new_y)
