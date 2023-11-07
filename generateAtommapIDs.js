const fs = require('fs');
const path = require('path');


//******除了此区域，其他代码请勿改动(coders unexpected)********//

const start = 10000  //要生成的编号的起始位置
const   end = 99999  //要生成的编号的结束位置
const svgFilePath = "./svgs/"  //存放svg的目录

//******************************************************//

var numberParam=5
try {
  const param = process.argv[2];

  // 检查参数是否存在且在1到10000之间
  if (param === undefined) {
    throw new Error('没有提供参数。');
  }
  numberParam = Number(param);

  if (isNaN(numberParam)) {
    throw new Error('参数不是一个有效的数字。');
  }

  if (numberParam < 1 || numberParam > 10000) {
    throw new Error('参数必须是一个1到10000之间的数字。');
  }

} catch (error) {
  console.error('发生错误：', error.message);
  process.exit(1);
}


function saveSVGFile(id) {
    // 确保svgs目录存在
    const dirPath = path.join(__dirname, svgFilePath);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }

    // 创建SVG内容
    const svgContent = `<svg width="200" height="50" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#ffffff"/>
        <text x="50%" y="50%" font-family="Arial" font-size="20" fill="black" dominant-baseline="middle" text-anchor="middle">${id}.atommap</text>
    </svg>`;

    // 设置文件路径
    const filePath = path.join(dirPath, `${id}.atommap.svg`);

    // 将SVG内容写入文件
    fs.writeFile(filePath, svgContent, (err) => {
        if (err) {
            console.error('Error writing SVG file:', err);
        } else {
            console.log(`SVG file saved as ${filePath}`);
        }
    });
}

var generateAtommapID = async () => {
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
    const result = getRandom(start,end)
    const isAvailable = await check(result)
    if(isAvailable) {
        console.log(`%c ${result}.atommap is OK to mint`,'color:green;')
        saveSVGFile(result)
    }else {
        console.log(`%c ${result}.atommap has been minted, ignored.`,'color:red;')
    }
    return isAvailable
}


for(let i=0;i<numberParam;i++){
	generateAtommapID()
}
