library(networkD3)

load("./master_data.rda")

shinyUI(fluidPage(
  
  verticalLayout(
    titlePanel('Identifier Prefix Checker'),
    selectInput('prefix', 'Prefix', c("No Filter",sort(unique(as.character(master_data$Prefix))))),
    dataTableOutput('table')
    
  )
)
)