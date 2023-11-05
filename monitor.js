const fs = require('fs');

var generateAtommap = async () => {
    var check = async (number) => {
        try {
            const res = await fetch(`https://geniidata.com/api/dashboard/chart/public/data?chartId=165760&pageSize=20&page=1&searchKey=atommapID&searchValue=` + number)
            const json = await res.json()
            const list = json['data']['list']
            return list.length === 0
        } catch (error) {
            console.log(error)
            return false
        }
    }
    function getRandom(n, m) {
        var num = Math.floor(Math.random() * (m - n + 1) + n)
        return num
    }
    const result = getRandom(999,9999)
    const isAvailable = await check(result)
    if(isAvailable) {
        console.log(`%c ${result}.atommap is OK to mint`,'color:green;')
    }else {
        console.log(`%c ${result}.atommap has been minted, please try again.`,'color:red;')
    }
}

var check = async (number) => {
    try {
        const res = await fetch(`https://geniidata.com/api/dashboard/chart/public/data?chartId=165760&pageSize=20&page=1&searchKey=atommapID&searchValue=` + number)
        const json = await res.json()
        const list = json['data']['list']
        return list.length === 0
    } catch (error) {
        console.log(error)
        return false
    }
}


function sendMessage(title, content) {
  const url = 'https://sctapi.ftqq.com/xxxx.send'; // xxxx换成自己的key
  const params = {
    title: title,
    desp: content
  };

  fetch(url, {
    method: 'POST', // 指定请求方法为POST
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded', // 指定内容类型为表单数据
    },
    body: new URLSearchParams(params).toString() // 将参数编码为字符串
  })
  .then(response => response.json()) // 解析返回的JSON数据
  .then(data => console.log(data)) // 打印返回的数据
  .catch(error => console.error('Error:', error)); // 错误处理
}

//load map id
var mapidlist = JSON.parse(process.env.mapid)
console.log(mapidlist)

//load id state
fs.readFile('state.json', 'utf8', (err, data) => {
  if (err) {
    console.error('Error reading the file:', err);
    return;
    }
  state = JSON.parse(data);
  console.log(state);
  checkIsAvailable(state);

});


async function checkIsAvailable(state){
    for(let i=0;i<mapidlist.length;i++){
        await check(mapidlist[i]).then(result=>{
            if(!result){ // if result==false
                
                if(state[mapidlist[i]]==false){

                }else{
                    sendMessage(mapidlist[i] + " is minted!","")
                    state[mapidlist[i]]=false
                    // 写入到state.json文件
                    const jsonContent = JSON.stringify(state);
                    fs.writeFile('state.json', jsonContent, 'utf8', function (err) {
                    if (err) {
                        console.log("An error occured while writing JSON Object to File.");
                        return console.log(err);
                    }
                    });
                }
            }
        })
      
    }
}

//checkIsAvailable()

