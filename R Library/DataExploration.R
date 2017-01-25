library(sqldf)
library(ggplot2)

# Generic Code to Summarize relationship of 2 data fields
funcCountRelationship_Counts = function(field1, field2, data){
  # Convert field names to strings
  print(paste("Report showing the count of ",field2," per ", field1))
  #field1 = deparse(substitute(field1))
  #field2 = deparse(substitute(field2))

  tempData = data
  variable1Name = paste(field2,"BY", field1, sep ="")

  sql = paste("SELECT [", field1, "], COUNT(DISTINCT([", field2, "])) as '", field2, "_Count' FROM tempData GROUP BY [", field1, "] ORDER BY COUNT(DISTINCT([", field2, "])) DESC", sep ="")

  results = sqldf(sql)

  var = assign(variable1Name, results)
  return(var)
}

funcRelationship_Distinct_Values = function(field1, field2, data){
  # Convert field names to strings
  #field1 = deparse(substitute(field1))
  #field2 = deparse(substitute(field2))

  tempData = data
  variable1Name = paste(field2,"BY", field1, sep ="")

  print(paste("This report shows the unique ", field2, " values associated with ", field1))
  sql = paste("SELECT [", field1, "], [", field2, "] as '", field2, "_Distinct_Values' FROM tempData GROUP BY [", field1, "],[",field2, "] ORDER BY [", field1, "] ASC", sep ="")

  results = sqldf(sql)

  var = assign(variable1Name, results)
  return(var)
}

funcExploreDataCountRelationships = function(dataSet){
  summary(dataSet)
  for(i1 in names(dataSet)){
    for(i2 in names(dataSet)){
      if(i1 != i2){
        output = funcCountRelationship_Counts(toString(i1), toString(i2), dataSet)
        print(output)
        ## Uncomment to print the reverse comparisons next to each other
        #outputReverse = funcRelationship(i2, i1, Size_Info_for_BM)
        #print(outputReverse)
      }
    }
  }
}

funcExploreDataDistinctRelationships = function(dataSet){
  summary(dataSet)
  for(i1 in names(dataSet)){
    for(i2 in names(dataSet)){
      if(i1 != i2){
        output = funcRelationship_Distinct_Values(toString(i1), toString(i2), dataSet)
        print(output)
        ## Uncomment to print the reverse comparisons next to each other
        #outputReverse = funcRelationship(i2, i1, Size_Info_for_BM)
        #print(outputReverse)
      }
    }
  }
}

funcGraphHistogramsForAllFields = function(dataSet){
  for(i in names(dataSet)){
    print(is.numeric(dataSet[i]))
    if(is.numeric(dataSet[i]))
      {
        mainTitle = paste(i, " Histogram")
        print(mainTitle)
        print(dataSet[i])
        hist(dataSet[i], main = mainTitle, xlab = paste(i))
      }
  }
}

#Use to copy table out of R and onto clipboard
copy.table <- function(obj, size = 4096) {
  clip <- paste('clipboard-', size, sep = '|')
  f <- file(description = clip, open = 'w')
  write.table(obj, f, row.names = TRUE, sep = '|')
  close(f)
}

