import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.linear_model import LinearRegression, Ridge, Lasso

class Regression_Processor():

    def __init__(self, data_train, data_test, label_list, regression_types_list, is_log_options, alpha_list):

        self.data_train = data_train
        self.data_test = data_test

        self.label_list = label_list
        self.regression_types_list = regression_types_list
        self.is_log_options = is_log_options
        self.alpha_list = alpha_list

        self.model_dict = {}
        self.num_models_complete = 0

        self.performance_df = pd.DataFrame(columns = ["post_period", "regression_type", "is_log", "alpha", "mse_test", "r2_train", "r2_test"])

        self.is_optimal_generated = False
        self.is_coefficient_df_generated = False

    def calculate_model_num(self):

        num_models = len(self.regression_types_list)
        num_labels = len(self.label_list)
        num_is_log_options = len(self.is_log_options)
        num_alphas = len(self.alpha_list)

        if "linear" in self.regression_types_list:
            self.num_models_total = (num_labels * num_is_log_options) * ( (num_alphas * (num_models - 1)) + 1)

        else:
            self.num_models_total = num_labels * num_is_log_options * num_alphas * num_models

    def print_updates(self):

        update_n = 10

        if (self.num_models_complete % update_n == 0) or (self.num_models_complete == self.num_models_total):
            print("{}/{} models processed".format(self.num_models_complete, self.num_models_total))

    def rename_performance_df_rows(self):

        self.performance_df["post_period"] = self.performance_df["post_period"].apply(lambda text: text.replace("review_count ", ""))

    def generate_model_iterations(self):

        #ITERATE OVER EACH PERIOD IN THE POST PERIOD
        for label_current in self.label_list:

            #IDENTIFY CURRENT LABEL & CREATE SPECIFIC TRAINING & TEST ARRAYS

            data_train_current = self.data_train.copy()
            data_test_current = self.data_test.copy()

            #CREATE VERSION THAT HAS CURRENT DATA ONLY
            for label in self.label_list:

                if label != label_current:
                    data_train_current.drop(columns = label, inplace = True)
                    data_test_current.drop(columns = label, inplace = True)

            x_train, y_train = data_train_current.drop(label_current,1), data_train_current[label_current]
            x_test, y_test = data_test_current.drop(label_current,1), data_test_current[label_current]

            #SET INITIAL OPTIMAL VALUES TO NONE
            optimal_model = None
            optimal_regression_type = None
            optimal_mse_test = None
            optimal_is_log = None
            optimal_alpha = None
            is_none = True

            #ITERATE THROUGH MODELS
            for regression_type in self.regression_types_list:
                for is_log in self.is_log_options:
                    for alpha_val in self.alpha_list:

                        if regression_type == "linear":
                            model = LinearRegression(normalize = True)

                        if regression_type == "ridge":
                            model = Ridge(normalize = True, alpha = alpha_val)

                        if regression_type == "lasso":
                            model = Lasso(normalize = True, alpha = alpha_val)

                        model.fit(x_train, y_train)
                        mse_test = metrics.mean_squared_error(y_test, model.predict(x_test))

                        if is_none:
                            optimal_model = model
                            optimal_mse_test = mse_test
                            optimal_regression_type = regression_type
                            optimal_is_log = is_log

                            if regression_type == "linear":
                                alpha_val = None

                            optimal_alpha = alpha_val

                            is_none = False

                        elif mse_test < optimal_mse_test:

                            optimal_model = model
                            optimal_mse_test = mse_test
                            optimal_regression_type = regression_type
                            optimal_is_log = is_log

                            if regression_type == "linear":
                                alpha_val = None

                            optimal_alpha = alpha_val

                        self.num_models_complete +=1

                        self.print_updates()

                        if regression_type == "linear":
                            break

            #GET METRICS FOR WINNING MODEL

            #mse_train = metrics.mean_squared_error(y_train, optimal_model.predict(x_train))
            mse_test = metrics.mean_squared_error(y_test, optimal_model.predict(x_test))
            r2_train = metrics.r2_score(y_train, optimal_model.predict(x_train))
            r2_test = metrics.r2_score(y_test, optimal_model.predict(x_test))

            metric_dict = {"post_period": label_current, "regression_type": optimal_regression_type, "is_log": optimal_is_log, "alpha": optimal_alpha, "mse_test": mse_test, "r2_train": r2_train, "r2_test": r2_test}
            self.performance_df = self.performance_df.append(metric_dict, ignore_index=True)
            self.model_dict[label_current] = optimal_model

    def get_optimal_models(self):

        if not self.is_optimal_generated:

            self.calculate_model_num()
            self.generate_model_iterations()
            self.rename_performance_df_rows()

            self.is_optimal_generated = True

        return self.performance_df, self.model_dict

    def get_coefficient_df(self):

        if not self.is_optimal_generated:
            self.get_optimal_models()

        coefficient_dict = {}

        for label in self.label_list:

            label_name = label.replace("review_count ", "")

            model = self.model_dict.get(label)
            coefficients = model.coef_
            intercept = model.intercept_

            coefficient_dict[label] = coefficients

        self.coefficient_df = pd.DataFrame.from_dict(coefficient_dict)

        feature_names = []

        for col in self.data_train.columns:
            if col in self.label_list:
                pass
            else:
                feature_names.append(col)

        self.coefficient_df["feature_name"] = feature_names
        self.coefficient_df.set_index("feature_name", inplace = True)

        return self.coefficient_df

    def print_top_coefficients(self, k = 10):

        for label in self.coefficient_df.columns:

            selected_df = self.coefficient_df.copy()

            abs_name = "{}_abs".format(label)

            selected_df[abs_name] = selected_df[label].apply(lambda val: abs(val))
            selected_df = selected_df[[label, abs_name]]
            selected_df.sort_values(by=abs_name, ascending=False, inplace = True)

            selected_df.drop(columns = abs_name, inplace = True)
            selected_df = selected_df.head(k)

            print(selected_df)

    def get_pre_period_importance(self):

        pre_period_coefficient_df = self.coefficient_df[self.coefficient_df.index.str.contains("review_count")]

        pre_period_coefficient_abs_df = pre_period_coefficient_df.copy()

        for col in pre_period_coefficient_abs_df:
            pre_period_coefficient_abs_df[col] = pre_period_coefficient_abs_df[col].apply(lambda val: abs(val))

        with sns.axes_style("white"):
            sns.heatmap(pre_period_coefficient_abs_df)

        plt.title("Historical Time Period Coefficients (Abs Value)")

        plt.show()

        return pre_period_coefficient_df
