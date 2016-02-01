library(dplyr)
library(stringdist)
library(networkD3)

load("./master_data.rda")

shinyServer(function(input, output) {
  
  # Combine the selected variables into a new data frame
  selectedData <- reactive({
    print(input$prefix)
    if(input$prefix=="No Filter")
      {
      master_data
    }
    else{
      
      unique(bind_rows(list
                       (
                       filter(master_data, Prefix == input$prefix),
                       filter(master_data, Prefix == tolower(input$prefix)),
                       filter(master_data, Prefix == toupper(input$prefix))
                       )
                       )
             )
      }
  }
  )
  
  output$table <- renderDataTable({
      selectedData()
  })
  
  
  
})