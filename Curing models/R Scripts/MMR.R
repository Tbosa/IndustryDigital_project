rm(list = ls())
rm(mlr)
##############################
library(car)
library(caret)
library(reshape2)

path_data <- 'C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data/Final tables'
setwd(path_data)
getwd()
##############################

Dapp <- read.csv(file = './App-Test datasets/Dapp.csv', sep = ';', header =  T)
Dtest <- read.csv(file = './App-Test datasets/Dtest.csv', sep = ';', header = T)
head(Dapp)[,1:3]
dim(Dapp)
dim(Dtest)

###
Dapp_sc <- preProcess(Dapp, method = c('center', 'scale'))
Dapp_stdz <- predict(Dapp_sc, Dapp)
Dtest_stdz <- predict(Dapp_sc, Dtest)

###
Y.sc_mx <- matrix(c(Dapp_sc$mean['Allgt_avg'], Dapp_sc$std['Allgt_avg'], Dapp_sc$mean['cont_100_avg'], Dapp_sc$std['cont_100_avg'],
                    Dapp_sc$mean['cont_rupt_avg'], Dapp_sc$std['cont_rupt_avg'], Dapp_sc$mean['durete_avg'], Dapp_sc$std['durete_avg']),
                  byrow = T, ncol = 2, dimnames = list(names(Dtest_stdz)[70:73], c('mean_app', 'stdev_app')))
RMSE_mx <- matrix(rep(NA, 4), 4, 1, dimnames = list(names(Dtest_stdz)[70:73], 'RMSE'))

###
mmr.init <- lm(cbind(Allgt_avg, cont_100_avg, cont_rupt_avg, durete_avg) ~ ., data = Dapp)
summary(mmr.init)

varcov_mx <- vcov(mmr.init)

#################################################################
#################################################################

###
mlr_allgt <- lm(Allgt_avg ~ ., data = Dapp_stdz[, -c(71:73)])
mlr_cont_100 <- lm(cont_100_avg ~ ., data = Dapp_stdz[, -c(70, 72, 73)])
mlr_cont_rupt <- lm(cont_rupt_avg ~ ., data = Dapp_stdz[, -c(70, 71, 73)])
mlr_durete <- lm(durete_avg ~ ., data = Dapp_stdz[, -c(70, 71, 72)])

###
mmr.1 <- lm(cbind(Allgt_avg, cont_100_avg, cont_rupt_avg, durete_avg) ~ ., data = Dapp_stdz)

#
all_res <- data.frame(mmr.1$residuals, mlr_allgt$residuals, mlr_cont_100$residuals, mlr_cont_rupt$residuals, mlr_durete$residuals)
names(all_res) <- c(paste("MMR - ", colnames(mmr.1$residuals)), paste("MLR - ", colnames(mmr.1$residuals)))
print(all_res)

cor(all_res[,1:4])

#
all_res <- data.frame(mmr.1$residuals, mlr_allgt$residuals, mlr_cont_100$residuals, mlr_cont_rupt$residuals, mlr_durete$residuals)
v
#
all_coef <- data.frame(mmr.1$coefficients, mlr_allgt$coefficients, mlr_cont_100$coefficients, mlr_cont_rupt$coefficients, mlr_durete$coefficients)
names(all_coef) <- c(paste("MMR - ", colnames(mmr.1$coefficients)), paste("MLR - ", colnames(mmr.1$coefficients)))
print(all_coef)

#
Y.mmr1 <- predict(mmr.1, Dtest_stdz[,-c(70:73)])

for (k in colnames(Y.mmr1)) {
  
  print(k)
  
  y.pred <- Y.mmr1[, k]
  y.pred <- (y.pred*Y.sc_mx[k, 2]) + Y.sc_mx[k, 1]
  y.obs <- Dtest[, k]
  RMSE <- RMSE(y.pred, y.obs)
  
  RMSE_mx[k, 1] <- round(RMSE,2)
  
}

print(RMSE_mx)

# shapiro.test(mmr.1$residuals[,1])
# shapiro.test(mmr.1$residuals[,2])
# shapiro.test(mmr.1$residuals[,3])
# shapiro.test(mmr.1$residuals[,4])

# mmr.1$residuals
# cbind(mmr.1$fitted.values)

varcov_mx <- vcov(mmr.1)
corr_mx <- cov2cor(varcov_mx)[-c(1,71, 141, 211),-c(1,71, 141, 211)]

corr_mx <- melt(corr_mx)
corr_mx[(corr_mx['value'] > 0.5 & corr_mx['value'] < 1) | (corr_mx['value'] < -0.5 & corr_mx['value'] > -1), c('Var1', 'Var2')]
ggplot(data = corr_mx, aes(Var1, Var2, filled = value)) + geom_tile()


##
par(mfrow = c(2,2))
coord_leg <- cbind(c(-3.6, -2, -1.2, 1), c(-1.5, -1.5, -2.5, 2.5))
row.names(coord_leg) <- names(Dapp)[70:73]
for (i in 1:4){
  
  target <- colnames(mmr.1$coefficients)[i]
  print(target)
  resid.df <- mmr.1$residuals[, i]
  fitval.df <- mmr.1$fitted.values[, i]
  
  resid_sderror <- round(summary(mmr.init)[[i]]$sigma, 2)
  rsquared <- round(summary(mmr.1)[[i]]$r.squared, 3)
  rsquared_adj <- round(summary(mmr.1)[[i]]$adj.r.squared, 3)
  
  plot(fitval.df, resid.df, type = "p", pch = 19, col = 'blue',
       main = paste(target), xlab = "standardized fitted values", ylab = " standardized residuals")
  abline(h = 0, col = "red", lty = 2)
  legend(coord_leg[target,1], coord_leg[target,2], legend = c(paste('R-squared : ', rsquared), paste('Adj-R : ', rsquared_adj), paste('Res SE : ', resid_sderror)), cex = 0.7, pt.cex = 1,
         box.lwd = 0, box.lty = 0, box.col = 'white', bg = 'white', bty = 'n', y.intersp = 0.5)
  
}

##########################
anova.mmr <- Anova(mmr.1)
summary(anova.mmr)

manova.mmr <- Manova(mmr.1)
print(manova.mmr)

###
lh.out_1 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Rotocure_RotoCylinderTemp_mean = 0"))
lh.out_1

lh.out_2 <- linearHypothesis(mmr, hypothesis.matrix = c("TS2_std = 0", "TS2_min = 0"))
lh.out_2

###
lh.out_1bis <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Extrud_ScrewSpeed_min = 0"))
lh.out_1bis

lh.out_3 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Caland_CylinderTemperatureLower_min = 0", "M_Caland_CylinderTemperatureLower_max = 0",
                                                        "M_Caland_CylinderTemperatureUpper_mean = 0", "M_Caland_CylinderTemperatureUpper_max = 0"))
lh.out_3

lh.out_4 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Rotocure_VulcPressure_mean = 0", "M_Rotocure_VulcPressure_stdev = 0",
                                                          "M_Rotocure_VulcPressure_min = 0", "M_Rotocure_VulcPressure_max = 0"))
lh.out_4

lh.out_5 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Extrud_BodyTemperature2_mean = 0", "M_Extrud_BodyTemperature2_max = 0"))
lh.out_5

lh.out_6 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Caland_OpeningLevelLeft_max = 0", "M_Caland_OpeningLevelLeft_stdev = 0"))
lh.out_6

lh.out_7 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Rotocure_CylPressureRight1_stdev = 0", "M_Rotocure_CylPressureRight1_min = 0",
                                                          "M_Rotocure_CylPressureRight1_max = 0"))
lh.out_7

lh.out_8 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Extrud_BodyTemperature1_mean = 0", "M_Extrud_BodyTemperature1_max"))
lh.out_8

lh.out_9 <- linearHypothesis(mmr.1, hypothesis.matrix = c("M_Rotocure_LineSpeed_mean = 0", "M_Rotocure_LineSpeed_stdev = 0",
                                                          "M_Rotocure_LineSpeed_min = 0", "M_Rotocure_LineSpeed_max = 0"))
lh.out_9

##
var <- c('M_Caland_CylinderTemperatureLower_min', 'M_Caland_CylinderTemperatureLower_max', 'M_Caland_CylinderTemperatureUpper_mean', 'M_Caland_CylinderTemperatureUpper_max', 
                  'M_Rotocure_VulcPressure_mean', 'M_Rotocure_VulcPressure_stdev', 'M_Rotocure_VulcPressure_min', 'M_Rotocure_VulcPressure_max', 'M_Extrud_BodyTemperature2_mean', 'M_Extrud_BodyTemperature2_max',
                  'M_Caland_OpeningLevelLeft_max', 'M_Caland_OpeningLevelLeft_stdev', 'M_Rotocure_CylinderTempLower_stdev', 'M_Extrud_PressureBeforeFilter_mean', 'M_Rotocure_CylPressureRight1_stdev',
                  'M_Rotocure_CylPressureRight1_min', 'M_Rotocure_CylPressureRight1_max')
var_tests <- c()
for (i in 1:length(var)) {
  var_tests[i] <- paste(var[i], '= 0') 
}
print(var_tests)

lh.out_10 <- linearHypothesis(mmr.1, hypothesis.matrix = var_tests)
lh.out_10

##################
mmr.final <- update(mmr.1, . ~ . - M_Caland_CylinderTemperatureLower_min - M_Caland_CylinderTemperatureLower_max - M_Caland_CylinderTemperatureUpper_mean -
                      M_Caland_CylinderTemperatureUpper_max - M_Rotocure_VulcPressure_mean - M_Rotocure_VulcPressure_stdev - M_Rotocure_VulcPressure_min -
                      M_Rotocure_VulcPressure_max - M_Extrud_BodyTemperature2_mean - M_Extrud_BodyTemperature2_max - M_Caland_OpeningLevelLeft_max -
                      M_Caland_OpeningLevelLeft_stdev - M_Rotocure_CylinderTempLower_stdev - M_Extrud_PressureBeforeFilter_mean -
                      M_Rotocure_CylPressureRight1_stdev - M_Rotocure_CylPressureRight1_min - M_Rotocure_CylPressureRight1_max)

print(Manova(mmr.final))



###
Y.pred <- predict(mmr.final, Dtest_stdz[,-(70:73)])

for (k in colnames(Y.pred)) {
  
  print(k)
  
  y.pred <- Y.pred[, k]
  y.pred <- (y.pred*Y.sc_mx[k, 2]) + Y.sc_mx[k, 1]
  y.obs <- Dtest[, k]
  RMSE <- RMSE(y.pred, y.obs)
  
  RMSE_mx[k, 1] <- RMSE
  
}

print(RMSE_mx)

#########

par(mfrow = c(2,2))
for (col in colnames(Y.pred)) {
  
  Y.pred[, col] <- (Y.pred[,col]*Y.sc_mx[col,2]) + Y.sc_mx[col,1]
  plot(Dtest[, col], Y.pred[, col], type = "p", pch = 19, col = "blue",
       xlab = "observed values", ylab = "predicted values", main = col)
  
}



