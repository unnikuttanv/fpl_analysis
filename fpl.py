#Notebook Config
import requests
import pandas as pd
import numpy as np
#%matplotlib inline
import matplotlib.pyplot as plt
plt.style.use('ggplot')
#API Set-Up

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json = r.json()

elements_df = pd.DataFrame(json['elements'])
element_types_df = pd.DataFrame(json['element_types'])
teams_df = pd.DataFrame(json['teams'])

main_df = elements_df[['web_name','first_name','team','element_type','now_cost','selected_by_percent','transfers_in','transfers_out','form','event_points','total_points','bonus','points_per_game','value_season','minutes','goals_scored','assists','ict_index','clean_sheets','saves']]


main_df = pd.merge(left=main_df,right=element_types_df[['id','singular_name']],left_on='element_type', right_on='id', how='left')
main_df = main_df.drop(["id", "element_type"],axis=1)
main_df = main_df.rename(columns = {'singular_name': 'position'})

main_df = pd.merge(left=main_df,right=teams_df[['id','name','played','strength_overall_away','strength_overall_home']],left_on='team', right_on='id', how='left')
main_df = main_df.drop(["id", "team"],axis=1)
main_df = main_df.rename(columns = {'name': 'team'})

main_df['value'] = main_df.value_season.astype(float)
main_df['ict_score'] = main_df.ict_index.astype(float)
main_df['selection_percentage'] = main_df.selected_by_percent.astype(float)
main_df['current_form'] = main_df.form.astype(float)
#Total Goals Contribution column = Goals + Assists
main_df['total_contribution']= main_df['goals_scored'] + main_df['assists']

#main_df = main_df.loc[sel_df.value > 0]
#preview of current state

main_df = main_df.rename(columns = {'singular_name': 'position'})
position_group = np.round(main_df.groupby('position', as_index=False).aggregate({'value':np.mean, 'total_points':np.sum}), 2)
position_group.sort_values('value', ascending=False)

team_group = np.round(main_df.groupby('team', as_index=False).aggregate({'value':np.mean, 'total_points':np.sum}), 2)
team_grp_df = team_group.sort_values('value', ascending=False)
team_grp_df['games_played'] = teams_df['played']
team_grp_df.head(5)

team_group = np.round(main_df.groupby('team', as_index=False).aggregate({'value':np.mean, 'total_points':np.sum}), 2)
team_grp_df = team_group
team_grp_df['games_played'] = teams_df['played']
team_grp_df['value_adjusted'] = np.round(team_grp_df['value']/teams_df['played'],2)
team_grp_df['points_adjusted'] = np.round(team_grp_df['total_points']/teams_df['played'],2)
team_grp_df.sort_values('points_adjusted',ascending=False).head(5)

fig,axes = plt.subplots(nrows=1, ncols=2, figsize=(20,7))
plt.subplots_adjust(hspace=0.25,  wspace=0.25)
team_grp_df.sort_values('value').plot.barh(ax=axes[0],x="team", y="value", subplots=True, color='#0087F1')
team_grp_df.sort_values('value_adjusted').plot.barh(ax=axes[1],x="team", y="value_adjusted", subplots=True, color='#2BBD00')
plt.ylabel("")
fig,axes = plt.subplots(nrows=1, ncols=2, figsize=(20,7))
plt.subplots_adjust(hspace=0.25,  wspace=0.25)
team_grp_df.sort_values('total_points').plot.barh(ax=axes[0],x="team", y="total_points", subplots=True, color='#EB2000')
team_grp_df.sort_values('points_adjusted').plot.barh(ax=axes[1],x="team", y="points_adjusted", subplots=True, color='#FF8000')
plt.ylabel("")
#plt.show()

gk_df = main_df.loc[main_df.position == 'Goalkeeper']
gk_df = gk_df[['web_name','team','selection_percentage','now_cost','clean_sheets','saves','bonus','total_points','value']]
def_df = main_df.loc[main_df.position == 'Defender']
def_df = def_df[['web_name','team','selection_percentage','now_cost','clean_sheets','assists','goals_scored','total_contribution','ict_score','bonus','total_points','value']]
mid_df = main_df.loc[main_df.position == 'Midfielder']
mid_df = mid_df[['web_name','team','selection_percentage','now_cost','assists','goals_scored','total_contribution','ict_score','current_form','bonus','total_points','value']]
fwd_df = main_df.loc[main_df.position == 'Forward']
fwd_df = fwd_df[['web_name','team','selection_percentage','now_cost','assists','goals_scored','total_contribution','ict_score','current_form','minutes','bonus','total_points','value']]
    


def plot(data=gk_df,x='now_cost',y='total_points',title='goalkeepers: total_points v cost'):
    ax = data.plot.scatter(x=x,y=y, alpha=.5, figsize=(20,9), title=title)
    for i, txt in enumerate(data.web_name):
        ax.annotate(txt, (data[x].iat[i],data[y].iat[i]))
    plt.grid(which='both', axis='both', ls='-')
    #plt.show()

plot()

topdef_df = def_df = def_df.loc[def_df.value > 3]
topdef_df = topdef_df = topdef_df.loc[def_df.total_contribution > 0]
plot(topdef_df,'now_cost','total_points','tp_vs_cost')

unluckydef_df = def_df.loc[def_df.ict_score > 10]
unluckydef_df.sort_values('ict_score', ascending=False).head(5)
plot(unluckydef_df,'ict_score','total_points','unlucky')

topmid_df = mid_df.loc[mid_df.ict_score > 25]
topmid_df = topmid_df.loc[mid_df.total_points > 15]
topmid_df.sort_values('total_points',ascending=False).head(5)
plot(topmid_df,'now_cost','total_points','top_mid')

topfwd_df = fwd_df[fwd_df.total_contribution > 0]
plot(topfwd_df,'now_cost','total_points','top_fwd')

top5_gk_df = gk_df.nlargest(5, 'value')
top5_def_df = def_df.nlargest(5, 'value')
top5_mid_df = mid_df.nlargest(5, 'value')
top5_fwd_df = fwd_df.nlargest(5, 'value')


ax = top5_gk_df.plot.scatter(x='value', y='total_points', color='DarkBlue', label='GK', s=top5_gk_df['value']*10, alpha=.5, figsize=(15,9), title="Top 5 Value Players by Position")
for i, txt in enumerate(top5_gk_df.web_name):
    ax.annotate(txt, (top5_gk_df.value.iat[i],top5_gk_df.total_points.iat[i]))
top5_def_df.plot.scatter(x='value', y='total_points', color='DarkGreen', label='DEF', s=top5_gk_df['value']*10, ax=ax)
for i, txt in enumerate(top5_def_df.web_name):
    ax.annotate(txt, (top5_def_df.value.iat[i],top5_def_df.total_points.iat[i]))
top5_mid_df.plot.scatter(x='value', y='total_points', color='DarkOrange', label='MID', s=top5_gk_df['value']*10, ax=ax)
for i, txt in enumerate(top5_mid_df.web_name):
    ax.annotate(txt, (top5_mid_df.value.iat[i],top5_mid_df.total_points.iat[i]))
top5_fwd_df.plot.scatter(x='value', y='total_points', color='DarkRed', label='FWD', s=top5_gk_df['value']*10, ax=ax)
for i, txt in enumerate(top5_fwd_df.web_name):
    ax.annotate(txt, (top5_fwd_df.value.iat[i],top5_fwd_df.total_points.iat[i]))

plt.show()




    
