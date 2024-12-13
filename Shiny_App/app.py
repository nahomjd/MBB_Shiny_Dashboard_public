import matplotlib.pyplot as plt
import pandas as pd
from shiny import reactive
from shiny.express import input, render, ui
import plotly.express as px
from support import conference, teams
from shinywidgets import render_plotly
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os

#comment to refresh
data = pd.read_csv('Season_Stats_23_24.csv')
data = data[data['Team'] != 'Le Moyne']
data = data.rename(columns={'Team AST': 'Ast', 'Team TRB': 'Trb', 'Team Shooting Total FG%': 'FG%'})
#print(data['NCAA Tournament'])

#function retrieves image 
def getImage(path):
    
    return OffsetImage(plt.imread(path), zoom=0.015, alpha = 1)
    
#Dashboard Header
ui.page_opts(title= "College Basketball Exporitory Dashboard")

#Side bar filters
with ui.sidebar():
    #Radio button for logo charts set to disable by default for memory concern
    ui.input_radio_buttons(
    "logo",
    ui.HTML("<span>Enable Logos (<span style='color:red;'>ONLY when a COUPLE conferences or Teams are SELECTED!</span>):</span>"),
    choices={
        "Disable": ui.HTML("<span style='color:green;'>Disable</span>"),
        "Enable": ui.HTML("<span style='color:red;'>Enable</span>")
    },
    selected='Disable'
    )
    
    #Team filter adds one team at a time, is searchable
    ui.input_selectize(  
    "team",  
    "Filter by Team",  
    teams,  
    multiple=True,  
    )  
    
    #Drop down menue to filter for all division 1 or just teams that missed or made the tournament
    ui.input_select('tournament', 'Filter by Making NCAA Tournament',\
                    choices={'True': 'In NCAA Tournament', 'False': 'Missed NCAA Tournament', 'All': 'All D1 Teams'}, multiple=False)
    
    #Confrence filter to pick individual confrences, is searchable
    ui.input_selectize('conference', 'Filter Confrences', choices=conference, multiple=True)


#KPI headers
with ui.layout_columns():
            
    with ui.value_box(
        theme="bg-gradient-orange-red", full_screen=True
    ):
        "Offensive KPIs"
        @render.ui  
        def Offense_select():
            #This should be a function its used in every dynamic visual
            if input.tournament() == 'All':
                input_df = data
                
            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]
            return f"Selected: {round(input_df['Pts'].mean(),2)} ppg, {round(input_df['Ast'].mean(),2)} ast, {round(input_df['Team ORB'].mean(),2)} orb"
       
       #KPI output
        f"D1 Avg.: {round(data['Pts'].mean(), 2)} ppg, {round(data['Ast'].mean(), 2)} ast,  {round(data['Team ORB'].mean(), 2)} orb"
            

    with ui.value_box(
        theme="text-green",
        full_screen=True,
    ):
        "Defensive KPIs"
        @render.ui  
        def Defensive_select():
            if input.tournament() == 'All':
                input_df = data

            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]
                
            return f"Selected: {round(input_df['Opponent Shooting Total FG%'].mean(),3)*100}% Opponent FG,\
                    {round(input_df['Team STL'].mean(),2)} stl, {round(input_df['Team BLK'].mean(),2)} blk, {round(input_df['Team DRB'].mean(),2)} drb"
       
        f"D1 Avg.: {round(data['Opponent Shooting Total FG%'].mean(),3)*100}% Opponent FG,\
                    {round(data['Team STL'].mean(),2)} stl, {round(data['Team BLK'].mean(),2)} blk, {round(data['Team DRB'].mean(),2)} drb"

    with ui.value_box(
        theme="purple", full_screen=True
    ):
        "Other KPIs"
        @render.ui  
        def other_select():
            if input.tournament() == 'All':
                input_df = data

            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]
            
            return f"Selected: {round(input_df['Miscellaneous Pace'].mean(),2)} pace, {round(input_df['Team TOV'].mean(),2)} tov,\
                    {round(input_df['Team Shooting Total FT%'].mean(),3)*100}% team FT"
        f"D1 Avg.: {round(data['Miscellaneous Pace'].mean(),2)} pace, {round(data['Team TOV'].mean(),2)} tov,\
                    {round(data['Team Shooting Total FT%'].mean(),3)*100}% team FT"
                    
#Matplotlib scatterplots that can have images
with ui.layout_columns(
    #col_widths={"sm": (5, 7, 12)},
    # row_heights=(2, 3),
    # height="700px",
):
    with ui.card(full_screen=True):
        @render.plot(width=750, height=750)  
        def plot():
            
            if input.tournament() == 'All':
                input_df = data

            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]
                
            #pts = input_df["Pts"]
            colors = ['#17becf', '#8b008b']
            labels = ['Missed NCAA Tournament', 'Made NCAA Tournament']
            i=0
            if input.logo() == 'Disable':
                fig, ax = plt.subplots()
                if input.tournament() == 'All':
                    for k, d in input_df.groupby('NCAA Tournament'):
                        ax.scatter(d['Pts'], d['SOS'], label=labels[i], c=colors[i], alpha=0.5)
                        i+=1
                    plt.legend(#bbox_to_anchor=(1.01, 1),
                         loc='upper left', borderaxespad=0, fontsize=10)  
                else:
                    ax.scatter(input_df['Pts'], input_df['SOS'], alpha=0.5, c='#17becf')
            elif input.logo() == 'Enable':
                fig, ax = plt.subplots(dpi=200)
                ax.scatter(input_df['Pts'], input_df['SOS'], alpha=0.5, c='white')
                for index, row in input_df.iterrows():

                    ab = AnnotationBbox(getImage(row['path']), (row['Pts'], row['SOS']), frameon=False)
                    ax.add_artist(ab)
            else:
                fig, ax = plt.subplots()
                if input.tournament() == 'All':
                    for k, d in input_df.groupby('NCAA Tournament'):
                        ax.scatter(d['Pts'], d['SOS'], label=labels[i], c=colors[i], alpha=0.5)
                        i+=1
                    plt.legend(#bbox_to_anchor=(1.01, 1),
                         loc='upper left', borderaxespad=0, fontsize=10)
                else:
                    ax.scatter(input_df['Pts'], input_df['SOS'], alpha=0.5, c='#17becf')
                
            ax.set_title("Points Per Game V. Schedule Strength")
            ax.set_xlabel("Points Per Game")
            ax.set_ylabel("Strength of Schedule")
           
            return fig
    
    with ui.card(full_screen=True):
        @render.plot(width=750, height=750)  
        def plot_2():
            if input.tournament() == 'All':
                input_df = data

            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]

            #pts = input_df["Pts"]
            colors = ['#17becf', '#8b008b']
            labels = ['Missed NCAA Tournament', 'Made NCAA Tournament']
            i=0
            if input.logo() == 'Disable':
                fig, ax = plt.subplots()
                
                if input.tournament() == 'All':
                    for k, d in input_df.groupby('NCAA Tournament'):
                        ax.scatter(d['Adjusted ORtg'], d['Adjusted DRtg'], label=labels[i], c=colors[i], alpha=0.5)
                        i+=1
                    plt.legend(#bbox_to_anchor=(1.01, 1),
                         loc='upper left', borderaxespad=0, fontsize=10)  
                else:
                    ax.scatter(input_df['Adjusted ORtg'], input_df['Adjusted DRtg'], alpha=0.5, c='#17becf')
            
            elif input.logo() == 'Enable':
                fig, ax = plt.subplots(dpi=200)
                ax.scatter(input_df['Adjusted ORtg'], input_df['Adjusted DRtg'], alpha=0.5, color='white')
                for index, row in input_df.iterrows():
                    #print(row['path'])
                    ab = AnnotationBbox(getImage(row['path']), (row['Adjusted ORtg'], row['Adjusted DRtg']), frameon=False)
                    ax.add_artist(ab)
            else:
                fig, ax = plt.subplots()
                
                if input.tournament() == 'All':
                    for k, d in input_df.groupby('NCAA Tournament'):
                        ax.scatter(d['Adjusted ORtg'], d['Adjusted DRtg'], label=labels[i], c=colors[i], alpha=0.5)
                        i+=1
                    plt.legend(#bbox_to_anchor=(1.01, 1),
                         loc='upper left', borderaxespad=0, fontsize=10)
                else:
                    ax.scatter(input_df['Adjusted ORtg'], input_df['Adjusted DRtg'], alpha=0.5, c='#17becf')
                
            #Invert the y axis so the better defensive teams are on the top
            ax.invert_yaxis()    
            ax.set_title('Offensive Vs Defensive Ratings', fontsize=24)
            fig.supxlabel('Higher is Better')
            fig.supylabel('Lower is Better')  
            ax.set_title("Defense V. Offense")
            ax.set_xlabel("Offensive Rating")
            ax.set_ylabel("Defensive Rating")
           
            return fig
 
 #plotly scatterplots that can have tooltips
with ui.layout_columns(
    #col_widths={"sm": (5, 7, 12)},
    # row_heights=(2, 3),
    # height="700px",
): 
    with ui.card(full_screen=True):
        @render_plotly
        def points_per_mov_sos():
            if input.tournament() == 'All':
                input_df = data

            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]
                
            fig = px.scatter(input_df, x="MOV", y="SOS",
                     width=800, height=400,
                         hover_name="Team")
            fig.update_layout(
                title='Victory Margin by Strength of Schedule',
                xaxis_title="Margin of Victory",
                yaxis_title="Strength of Schedule"
            )
            
            return fig
            
    with ui.card(full_screen=True):
        @render_plotly
        def shooting_3pt():
            if input.tournament() == 'All':
                input_df = data

            else:
                input_df = data[data['NCAA Tournament'].astype(str) == input.tournament()]
            
            if len(input.team()) != 0:
                input_df =  input_df[input_df['Team'].isin(input.team())]
            if len(input.conference()) != 0:
                input_df =  input_df[input_df['Conf'].isin(input.conference())]
                
            fig = px.scatter(input_df, x="Miscellaneous Pace", y="Team 3PA", color="Team Shooting Total 3P%",
                    hover_name="Team", width=800, height=400)
            
            fig.update_layout(
                title='Speed of Three Point Shooting',
                xaxis_title="Possessions a Game",
                yaxis_title="3-Point Attempts a Game"
            )
            
            return fig
 
 #Datatable output, is not dynamic, but can be filtered
@render.data_frame
def stats_df():
    view_cols = ['Team', 'Conf', 'W', 'G', 'L', 'Pts', 'Ast', 'Trb', 'FG%', 'NCAA Tournament']
    return render.DataTable(data[view_cols], filters=True, selection_mode='rows')
    

#Download button, simply downloads entire source file, no dynamic filters
@render.download(label="Download CSV")
def download1():

    path = os.path.join(os.path.dirname(__file__), "Season_Stats_23_24.csv")
    return path