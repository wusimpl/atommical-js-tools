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
    return isAvailable
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

generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
generateAtommap()
