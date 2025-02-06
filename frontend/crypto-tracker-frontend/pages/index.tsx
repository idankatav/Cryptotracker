import React, { useState, useEffect } from "react";
import { searchCrypto, getCryptoDetails, getCryptoHistory } from "../api/crypto";
import { TextField, Typography, Card, CircularProgress, Autocomplete, Container, Box } from "@mui/material";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Home() {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedCrypto, setSelectedCrypto] = useState<any>(null);
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (query.length > 1) {
      handleSearch();
    } else {
      setSearchResults([]);
    }
  }, [query]);

  const handleSearch = async () => {
    if (!query) {
        setError("Please enter a search term.");
        return;
    }
    setLoading(true);
    try {
        const results = await searchCrypto(query);
        if (results.length === 0) {
            setError("No cryptocurrencies found.");
        } else {
            setError("");
        }
        setSearchResults(results);
    } catch (err) {
        setError("Error fetching data. Try again.");
    }
    setLoading(false);
};


  const handleSelectCrypto = async (cryptoId: string) => {
    setLoading(true);
    try {
      const details = await getCryptoDetails(cryptoId);
      setSelectedCrypto(details);
      const history = await getCryptoHistory(cryptoId, 7);
      setHistoryData(history.map((point: any) => ({ date: new Date(point.timestamp).toLocaleDateString(), price: point.price })));
    } catch (err) {
      setError("Error fetching details. Try again.");
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="md" sx={{ padding: 3, backgroundColor: "#1e1e1e", minHeight: "100vh", color: "#fff", borderRadius: 2 }}>
      <Typography variant="h4" align="center" sx={{ fontWeight: "bold", mb: 2 }}>
        Crypto Price Tracker
      </Typography>

      <Autocomplete
        options={searchResults}
        getOptionLabel={(option: any) => option.name}
        sx={{ backgroundColor: "#fff", borderRadius: 2, mb: 2 }}
        onInputChange={(event, value) => setQuery(value)}
        onChange={(event, newValue) => newValue && handleSelectCrypto(newValue.id)}
        renderInput={(params) => <TextField {...params} label="Search Cryptocurrency" variant="outlined" fullWidth />}
      />

      {error && <Typography color="error">{error}</Typography>}
      {loading && <CircularProgress sx={{ display: "block", mx: "auto", mt: 2 }} />}

      {selectedCrypto && (
        <Card sx={{ padding: 3, mt: 3, backgroundColor: "#333", color: "#fff" }}>
          <Typography variant="h5">{selectedCrypto.name} ({selectedCrypto.symbol})</Typography>
          <Typography>Price: ${selectedCrypto.price}</Typography>
          <Typography>Market Cap: ${selectedCrypto.market_cap}</Typography>
          <Typography>24h High: ${selectedCrypto.high_24h}</Typography>
          <Typography>24h Low: ${selectedCrypto.low_24h}</Typography>

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">7-Day Price Chart</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historyData}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </Card>
      )}
    </Container>
  );
}
