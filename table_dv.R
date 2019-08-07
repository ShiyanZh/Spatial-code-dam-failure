# author @Shiyan
# R practicein
# load libraries
library(raster)
library(rgdal)

# open raster data
dv_flood <- raster(x = "D:/GWU/AdamJ/task6/mission/flood_dv2.tif")

# Create category matrix
reclass_dv <- c(-Inf, 20, 1,
                20, 40, 2,
                40, Inf, 3)

reclass_dv_m <- matrix(reclass_dv,
                    ncol = 3,
                    byrow = TRUE)

# Reclassify raster
dv_classified <- reclassify(dv_flood,
                             reclass_dv_m)

# Create a dataFrame to display and calculate other need value 
tbl_dv <- data.frame(freq(dv_classified))
# Delete the no data value
tbl_dv <- tbl_dv[-c(4), ]
# Add range and percentage column to the original dataFrame
tbl_dv <- data.frame(tbl_dv,
                        range = c("0-20","20-40","over_40"),
                        percentage = tbl_dv$count / sum(tbl_dv$count))

# Save the completed table into a csv file
write.csv(tbl_dv, file = "D:/GWU/AdamJ/task6/mission/result/DV2_stats.csv")
# Show the table in the console
print(tbl_dv)

# Set the location and name of barplot result
png(filename="D:/GWU/AdamJ/task6/mission/result/DV2_hist.png")

# Barplot the histogram of DV value distribution
dv_hist <- barplot(tbl_dv$percentage,
                   main="Distribution of DV Values",
                   xlab="DV Value Range",
                   ylab="Distribution Percentage",
                   names.arg = c("0-20","20-40","over_40"),
                   border="red",
                   col="orange")

# Save the png file
dev.off()




