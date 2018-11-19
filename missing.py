import random
def get_missing(number, percentage):
    """
        TESTING. returns id numbers of missing values. Purpose - fix missing values for testing

        Parameters
        ----------
        percentage : float
            Number from 0 to 1 that is percent of data missing
        number: int
            total number of samples

        Returns
        -------
        list
            list of integers that are indices of missing samples
        """
    number_missing = int(number * percentage)
    missing_id = random.randint(0, number - 1)
    result=[]
    result.append(missing_id)
    for i in range(1,number_missing):
        missing_id = random.randint(0, number - 1)
        while missing_id in result:
            missing_id = random.randint(0, number - 1)
        result.append(missing_id)
    return result

'''number_missing = int(65 * 0.25)
result=[]
for i in range(0,number_missing):
   missing_id=random.randint(20,65)
   result.append(missing_id)
print(result)'''

print(get_missing(45,0.3))