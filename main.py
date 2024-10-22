from shiny import App, ui, render, reactive
import random
from functools import lru_cache
import matplotlib.pyplot as plt


CLUSTER_CONFIGS = [
    (1,1, 'Single Instance'),
    (3,4, "3 out of 4"),
    (5,7, "5 out of 7"),
    (7,10, "7 out of 10"),
]

@lru_cache
def simulate_bft_system(num_servers, mtbf, mttr, total_time=100000):
    uptime_timeseries = []
     # start servers as Down so that on time 0 they go up and receive a time to next downtime
    server_states = [False] * num_servers
    server_countdowns = [0] * num_servers
    
    for _ in range(total_time):
        for i in range(num_servers):
            if server_countdowns[i] == 0:
                if server_states[i]:  # Server goes down
                    downtime = int(random.expovariate(1 / mttr))
                    server_countdowns[i] = downtime
                    server_states[i] = False
                else: # Server comes back up
                    uptime = int(random.expovariate(1 / mtbf))
                    server_countdowns[i] = uptime
                    server_states[i] = True
            else:
                server_countdowns[i] -= 1
        
        uptime_timeseries.append(tuple(server_states))
        
    return uptime_timeseries


app_ui = ui.page_fluid(
    ui.h2("Byzantine Fault Tolerance Simulation"),
    
    ui.page_sidebar(
        ui.sidebar(
            ui.input_numeric("total_time", "hours of simulation", min=1000, max=1_000_000, value=10_000, step=1000),
            ui.input_slider("monthly_failure_freq", "Monthly failures", min=1, max=100, value=2),
            ui.input_slider("hours_to_fix", "Time to fix in hours", min=1, max=100, value=2),
        ),
        ui.output_plot("bft_plot", height="400px"),
        ui.output_ui("availability"),
    )
)

def server(input, output, session):        
    def get_mtbf(monthly_failure_freq):
        HOURS_PER_MONTH = 365.25 * 24 / 12
        return HOURS_PER_MONTH / monthly_failure_freq

    @reactive.Calc
    def simulation_result():
        mtbf = get_mtbf(input.monthly_failure_freq())
        mttr = input.hours_to_fix()
        return simulate_bft_system(10, mtbf, mttr, input.total_time())


    @output
    @render.plot
    def bft_plot():
        result = simulation_result()
        x = list(range(len(result)))
        
        fig, ax = plt.subplots()
        for M,N, label in CLUSTER_CONFIGS:
            y = [1 if sum(instances[:N]) >= M else 0 for instances in result]
            ax.plot(x, y, label=label, linestyle='-')

        ax.set_xlabel("Time")
        ax.set_ylabel("Uptime (1 = Up, 0 = Down)")
        ax.set_title("BFT System Uptime Across Cluster Settings")
        ax.legend()
        
        return fig

    @output
    @render.ui
    def availability():
        result = simulation_result()
        uptimes = [
            "<p>for {} configuration: {:.4%}</p>".format(label, len([1 for x in result if sum(x[:N]) >= M]) / len(result))
            for M,N,label in CLUSTER_CONFIGS
        ]

        return ui.HTML("<h3>System Availability:</h3>"+"\n".join(uptimes))

app = App(app_ui, server)

# To run the app:
# shiny run --reload main.py
