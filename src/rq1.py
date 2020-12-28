import pandas as pd 


# a TS fails for any Ruby version for a specific GEM configuration
def tag_necessary(df, groupby_columns):
    for name, group in df.groupby(groupby_columns):
        if (group['build_status'] == "failed").all():
            df.loc[group.index, 'is_necessary'] = False
            df.loc[group.head(1).index, 'is_necessary'] = True 

    #df.loc[df['is_necessary'] == False]
    return df


if __name__ == "__main__": 
    dataset_rail_complete = '../output/cleaned_dataset_rail_100000_new_noindex.csv'
    df = pd.read_csv(dataset_rail_complete, sep=';', header = 0)
    print(df.shape[0])
    #columns = ['test_suite','job_env']
    #columns = ['test_suite','job_rvm']
    #columns = ['test_suite']
    df = tag_necessary(df, ['test_suite'])
    print(len(df.loc[df['is_necessary'] == False]))
    print("world")
    #calculate_gem_ruby_1(df)  a TS fails for any Ruby version for a specific GEM configuration 265  /  1515
    #calculate_gem_ruby_2(df)  a TS fails for any GEM configuration for a specific Ruby version 2016  /  4193
    #calculate_gem_ruby_3(df)  a tS fails for any GEM configuration for any Ruby version 99  /  871
    
