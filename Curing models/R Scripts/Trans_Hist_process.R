rm(list = ls())
rm()

options(digits.sec = 3)
getOption("digits.sec")
if(!require(openxlsx))
  install.packages("openxlsx")
require(openxlsx)

setwd(dir = "C:/Users/barbosaa01/Documents/Mars-Avril 2018/Thesis project")
getwd()

###############################################################################
df_data_types <- function(df) {
  
  i <- 1
  while(i <= ncol(df)) {
    
    print(i)
    if(names(df[, i, drop = FALSE]) == "timestamp") {
      df$timestamp <- as.POSIXct(x = df$timestamp, format = "%Y-%m-%d %H:%M:%S", tz = "")
      
      i <- i + 1
      next;
    }
    
    else {
      df[,i] <- as.factor(df[,i])
      
      i <- i + 1
      next;
    }
    
  }
  
  str(df)
  return(df)
}
###############################################################################


#############################################################################################################
#############################################################################################################
T_histo <- readWorkbook(xlsxFile = paste0("./MES Prod/", "20170825_VDR_Transaction_History.xlsx"), sheet = 1, colNames = TRUE, skipEmptyRows = T)                        
str(T_histo) # n = 641 784 / p = 26
T_histo <- T_histo[,-18] # there are two "equipment"-named columns --> deleting first 'equipment' column with 'NULL' values only

full_NA_cols <- names(which(sapply(T_histo, function(x) sum(is.na(x))) == nrow(T_histo)))
full_NULL_cols <- names(which((sapply(T_histo, function(x) sum(ifelse(x == "NULL",1,0))) == nrow(T_histo)) == TRUE))
T_histo <- T_histo[, !colnames(T_histo) %in% c(full_NULL_cols, full_NA_cols)] # -> p = 25

# Deleting not informative columns
T_histo <- subset(T_histo, select = -c(id, atr_name, subtype, quality.status, bachexpirydate,
                                       location, user, tank, workstation, avg.scrap,
                                       quality.new, weight)) # -> p = 9

#
T_histo_V62003 <- subset(T_histo, subset = (equipment == "V62003"))
hist_LVC3_403E <- T_histo_V62003[grepl(pattern = "403E" , x = T_histo_V62003$description),]
hist_LVC3_403E <- subset(hist_LVC3_403E, subset = (reason == "production" | reason == "consumption"))

starting_date <- as.POSIXct(strptime("2016-12-01 00:00:00", "%Y-%m-%d %H:%M:%S"))
end_date <- as.POSIXct(strptime("2017-06-01 00:00:00", "%Y-%m-%d %H:%M:%S"))

as.numeric(starting_date)
hist_LVC3_403E <- subset(hist_LVC3_403E, subset = (timestamp >= as.numeric(starting_date)) &
                           (timestamp <= as.numeric(starting_date)))
#######################



