import numpy as np

def parse_related_properties(property, dic, def_val, is_float = False, is_exp = False):
    if property in dic:
        return [dic[property]]
    elif property+"_array" in dic:
        return dic[property+'_array']
    elif property+"_lowerlimit" in dic or property+"_lowerlimit" in dic:                    
        if property+"_lowerlimit" in dic:
            l = dic[property+'_lowerlimit']
        else:
            raise ValueError(error.errors['missing_lower_limit'] + ' for property' + property)
        if property+"_upperlimit" in dic:
            u = dic[property+'_upperlimit']
        else:
            raise ValueError(error.errors['missing_upper_limit'] + ' for property' + property)
        if is_exp:
            if property+"_step" in dic:
                i = dic[property+'_step']
                steps = int(round((u-l+1)/i)) + 1
                return np.logspace(l, u, steps)
            else:
                return np.logspace(l, u, u-l+1)
        else:
            if is_float == False:
                if property+"_step" in dic:
                    i = dic[property+'_step']
                    return np.arange(l, u, i)
                else:
                    return np.arange(l, u)
            else:
                if property+"_n_steps" in dic:
                    n = dic[property+'_n_steps']
                    return np.linspace(l, u, n)
                else:
                    return np.linspace(l, u)
    else:
        return [def_val]