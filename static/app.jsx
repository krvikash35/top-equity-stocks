function StockTable(props){
    const stocks = props.stocks;
    const stock = stocks.map((s) => 
            <tr key={s.code}>
                <td>{s.code}</td>
                <td>{s.name}</td>
                <td>{s.open}</td>
                <td>{s.high}</td>
                <td>{s.low}</td>
                <td>{s.close}</td>
            </tr>
        );
    return (
        <table className="stockTable">
            <thead> 
                <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Open</th>
                    <th>High</th>
                    <th>Low</th>
                    <th>Close</th>
                </tr>
            </thead>
            <tbody>
                {stock}
            </tbody>
        </table>
    );
}

class SearchStocks extends React.Component {
    constructor(){
        super();
        this.state = {
            isGetSearchResultPending: false,
            stocks: [],
            noResultMsg: 'Search result will apear here'
        }

        this.onSearchStocks = this.onSearchStocks.bind(this);
    }

    componentDidMount(){

    }

    async onSearchStocks(e){
        if( e.keyCode == 13){
            const stockName = e.target.value
            e.target.value=null
            this.setState({
                isGetSearchResultPending: true
            })
            const response = await axios.get('/api/searchstocks?name='+stockName);
            this.setState({
                isGetSearchResultPending: false,
                stocks: response.data,
                noResultMsg: 'No record found!'
            });
        }
    }

    render() {
        const {stocks, noResultMsg, isGetSearchResultPending} = this.state;
        return (
            <div>
                <div className="searchStocksHdrs"> 
                    <div className="searchStocksHdrsText">Search stocks</div>
                    {isGetSearchResultPending && <div className="spinner"></div>}
                </div>
                <input  className="searchStocksInput" onKeyDown={this.onSearchStocks} placeholder="Search stock detail by name i.e type BOSCH LTD and hit enter key" />
            { stocks.length === 0? (
                <div className="noSearchStocksText">{noResultMsg}</div>
            )   :   (
                <StockTable stocks={stocks}/>
            )}
            </div>
        )
    }
}


class TopStocks extends React.Component {
    constructor(){
        super();
        this.state = {
            getTopStocksPending: false,
            stocks: []};
    }

    async componentDidMount() {
        this.setState({getTopStocksPending: true})
        const topstocks = await axios.get('/api/topstocks')
        this.setState({
            getTopStocksPending: false,
            stocks: topstocks.data
        })
        
    }

    render() {
        const isGetTopStocksPending = this.state.getTopStocksPending
        const stocks = this.state.stocks;
        return (
            <div className="topStocksComponent">
                <div className="searchStocksHdrs"> 
                    <div className="searchStocksHdrsText">Top stocks</div>
                    {isGetTopStocksPending && <div className="spinner"></div>}
                </div>
                {!isGetTopStocksPending && <StockTable stocks={stocks}/>}   
            </div>
        )
    }
}



const App = function() {
    return (
        <div>
            <p>
                Search stock details by name or/and get top 10 equity stock details based on last trading day data. 
                Top stocks are decided on basis of %change in closing price from opening price using formule <code>((Close-Open)/Open)*100</code>.
                This application update data from bseindia bhavcopy every day at 6PM IST.
            </p>
            <SearchStocks/>
            <TopStocks/>
        </div>
    )
}

ReactDOM.render(
    <App />,
    document.getElementById('root')
  );