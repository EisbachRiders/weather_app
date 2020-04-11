
import React, { useEffect, useState } from 'react'


function App() {
  // const [data,setData] = useState(null)
  const [water, setWater] = useState('')
  const [water2, setWater2] = useState('')

  // async function fetchUrl(url) {
  //   const response = await fetch(url)
  //   const json = await response.json()
  //   setData(json)
  // }

  const getWaterData = value => {
    let waterTemp = null
    let waterTime = null
    if (
      value
        .split('table')[7]
        .split('<td  class="center">')[1]
        .split('</td>')[0] !== '--'
    ) {
      waterTemp = value
        .split('table')[7]
        .split('<td  class="center">')[1]
        .split('</td>')[0]
      waterTime = value
        .split('table')[7]
        .split('<td  class="center">')[0]
        .split('<td >')[1]
        .split('</td>')[0]
    } else if (
      value
        .split('table')[7]
        .split('<td  class="center">')[2]
        .split('</td>')[0] !== '--'
    ) {
      waterTemp = value
        .split('table')[7]
        .split('<td  class="center">')[2]
        .split('</td>')[0]
      waterTime = value
        .split('table')[7]
        .split('<td  class="center">')[1]
        .split('<td >')[1]
        .split('</td>')[0]
    } else if (
      value
        .split('table')[7]
        .split('<td  class="center">')[3]
        .split('</td>')[0] !== '--'
    ) {
      waterTemp = value
        .split('table')[7]
        .split('<td  class="center">')[3]
        .split('</td>')[0]
      waterTime = value
        .split('table')[7]
        .split('<td  class="center">')[2]
        .split('<td >')[1]
        .split('</td>')[0]
    }
    return [waterTemp, waterTime]
  }

  useEffect(() => {
    const proxyurl = 'https://cors-anywhere.herokuapp.com/'
    const urlWater =
      'https://www.gkd.bayern.de/en/rivers/watertemperature/kelheim/muenchen-himmelreichbruecke-16515005/current-values/table'
    const urlWater2 =
      'https://www.gkd.bayern.de/en/rivers/watertemperature/kelheim/muenchen-tieraerztl-hochschule-16516008/current-values/table'
    const fetchData1 = () => {

      fetch(proxyurl + urlWater)
        .then(function(response) {
          return response
        })
        .then(response => response.text())
        .then(contents => {
          let waterData = getWaterData(contents)
          setWater(waterData[0])

        })
        .catch(function(e) {
          console.log(e)
        })
    }
    fetchData1()
    const fetchData2 = () => {

      fetch(proxyurl + urlWater2)
        .then(function(response) {
          return response
        })
        .then(response => response.text())
        .then(contents => {
          let waterData = getWaterData(contents)
          setWater2(waterData[0])
        })
        .catch(function(e) {
          console.log(e)
        })
    }
    fetchData2()
  }, [])
  const output = water || water2

  return (<p>
    {output}

  </p>)
   
  
}

export default App

