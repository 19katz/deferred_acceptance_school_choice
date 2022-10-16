import itertools
import random
import numpy as np
import os
import sys
from deferred_acceptance import deferred_acceptance
from utils import create_dataframes

class Student:
    def __init__(self, name, permutations, minority):
        self.name = name
        self.alpha = 0
        self.beta = 0
        self.min = minority
        self.school_pref = list(random.sample(permutations, 1)[0])
    
    def set_alpha_beta(self, alpha_mean_maj, alpha_std, beta_std):
        self.beta = np.random.normal(0, beta_std)

        if self.min:
            self.alpha = np.random.normal(0, alpha_std)
        else:
            self.alpha = np.random.normal(alpha_mean_maj, alpha_std)

def create_students(num_students, schools, fraction_min, alpha_mean_maj, alpha_std, beta_std):
    students_list = []
    for i in range(num_students):
        student_name = "s" + str(i + 1)
        students_list.append(student_name)
    min_students = random.sample(students_list, int(num_students * fraction_min))

    students = []
    for s in students_list:
        is_min = (s in min_students)
        student = Student(s, schools, is_min)
        student.set_alpha_beta(alpha_mean_maj, alpha_std, beta_std)
        students.append(student)
    
    student_preferences = {}

    for s in students:
        student_preferences[s.name] = s.school_pref

    return students, student_preferences

def create_school_rankings(students, aff_act, schools):
    scores = []
    indices = []
    aff_act_scores = []
    for i in range(0, len(students)):
        indices.append(i + 1)
        scores.append(students[i].alpha + students[i].beta)
        aff_act_scores.append(students[i].beta)

    scores, new_indices = (list(t) for t in zip(*sorted(zip(scores, indices), reverse=True)))
    aff_act_scores, aff_act_indices = (list(t) for t in zip(*sorted(zip(aff_act_scores, indices), reverse=True)))

    school_preferences = {}
    for i in range(len(schools)):
        if i == 0 and aff_act:
            school_preferences[schools[i]] = aff_act_indices
        else:
            school_preferences[schools[i]] = new_indices

    return school_preferences

def simple_school_choice(schools_list, schools_quota, students_list, schools_preferences, students_preferences) -> None:
    """
    Here is a minimalistic example of deferred acceptance algorithm for school choice.
    """
    # Prepare the dataframes

    students_df, schools_df = create_dataframes(
        students_list=students_list,
        students_preferences=students_preferences,
        schools_list=schools_list,
        schools_preferences=schools_preferences,
    )

    matches = deferred_acceptance(
        students_df=students_df, schools_df=schools_df, schools_quota=schools_quota
    )

    return matches

def check_minority_student_welfare(min_student, normal_match, aff_act_match):
    normal_ranking = -1
    aff_act_ranking = -1
    for key in normal_match:
        if min_student in key:
            normal_ranking = normal_match[key][0]
    for key in aff_act_match:
        if min_student in key:
            aff_act_ranking = aff_act_match[key][0]
    
    return (normal_ranking < aff_act_ranking)


if __name__ == "__main__":
    schools_list = ['c1', 'c2']
    schools_quota = {"c1": 1, "c2": 2}
    num_students = 3
    fraction_min = 0.34
    alpha_mean_maj = 3
    alpha_std = 1
    beta_std = 1

    num_same = 0
    num_diff = 0

    num_unchanged = 0
    num_benefit = 0
    num_worsened = 0

    for i in range(500):
        print(i)

        school_permutations = list(itertools.permutations(range(1, len(schools_list) + 1)))
        students, students_preferences = create_students(num_students, school_permutations, fraction_min, alpha_mean_maj, alpha_std, beta_std)
        schools_preferences = create_school_rankings(students, False, schools_list)
        aff_act_schools_preferences = create_school_rankings(students, True, schools_list)
        students_list = [s.name for s in students]
        students_score = [s.alpha + s.beta for s in students]
        aff_act_score = [s.beta for s in students]
        min_students = []

        for student in students:
            if student.min == True:
                min_students.append(student.name)

        print(min_students)
        print(students_preferences)
        print(schools_preferences)
        print(aff_act_schools_preferences)

        normal_match = simple_school_choice(schools_list, schools_quota, students_list, schools_preferences, students_preferences)
        aff_act_match = simple_school_choice(schools_list, schools_quota, students_list, aff_act_schools_preferences, students_preferences)

        normal_match_keys = list(normal_match.keys())
        aff_act_match_keys = list(aff_act_match.keys())
        print(normal_match_keys)
        print(aff_act_match_keys)
        print(aff_act_match)

        if normal_match_keys == aff_act_match_keys:
            num_same += 1
            num_unchanged += len(min_students)
        else:
            num_diff += 1
            for student in min_students:
                min_improve = check_minority_student_welfare(student, normal_match, aff_act_match)
                if min_improve:
                    num_

            


    print(num_same)
    print(num_diff)

    
