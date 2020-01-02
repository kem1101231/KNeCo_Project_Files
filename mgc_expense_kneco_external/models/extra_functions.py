import datetime

class ExtraFunction:

	def add_days(from_date, add_days):
	    business_days_to_add = add_days
	    current_date = from_date
	    while business_days_to_add > 0:
	        current_date += datetime.timedelta(days=1)
	        weekday = current_date.weekday()
	        if weekday >= 5: # sunday = 6
	            continue
	        business_days_to_add -= 1
	    return current_date
