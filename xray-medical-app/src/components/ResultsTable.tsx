import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  TableSortLabel,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Avatar,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  CheckCircle as NormalIcon,
  Error as AbnormalIcon,
  Warning as WarningIcon,
  GetApp as ExportIcon,
} from '@mui/icons-material';
import { TableViewData } from '../types';

interface ResultsTableProps {
  data: TableViewData[];
  onViewDetails: (id: string) => void;
  onExportData?: () => void;
}

type Order = 'asc' | 'desc';
type OrderBy = keyof TableViewData;

const ResultsTable: React.FC<ResultsTableProps> = ({
  data,
  onViewDetails,
  onExportData,
}) => {
  const [order, setOrder] = useState<Order>('desc');
  const [orderBy, setOrderBy] = useState<OrderBy>('uploadTime');
  const [filterText, setFilterText] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'normal' | 'abnormal'>('all');

  const handleRequestSort = (property: OrderBy) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const getStatusIcon = (status: 'normal' | 'abnormal') => {
    return status === 'normal' 
      ? <NormalIcon color="success" sx={{ fontSize: 18 }} />
      : <AbnormalIcon color="error" sx={{ fontSize: 18 }} />;
  };

  const getStatusChip = (status: 'normal' | 'abnormal') => {
    return (
      <Chip
        icon={getStatusIcon(status)}
        label={status.toUpperCase()}
        color={status === 'normal' ? 'success' : 'error'}
        size="small"
        sx={{ fontWeight: 500 }}
      />
    );
  };

  const getSpacingStatus = (value: number, normal: boolean = true) => {
    const isNormal = value >= 4.0 && value <= 8.0;
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {value.toFixed(1)} mm
        </Typography>
        {isNormal ? (
          <NormalIcon color="success" sx={{ fontSize: 16 }} />
        ) : (
          <AbnormalIcon color="error" sx={{ fontSize: 16 }} />
        )}
      </Box>
    );
  };

  const filteredData = data.filter(item => {
    const matchesText = item.imageName.toLowerCase().includes(filterText.toLowerCase()) ||
                       item.abnormalities.some(abnormality => 
                         abnormality.toLowerCase().includes(filterText.toLowerCase())
                       );
    const matchesStatus = statusFilter === 'all' || item.overallStatus === statusFilter;
    return matchesText && matchesStatus;
  });

  const sortedData = filteredData.sort((a, b) => {
    let aValue = a[orderBy];
    let bValue = b[orderBy];

    // Handle array fields
    if (orderBy === 'abnormalities') {
      aValue = a.abnormalities.length;
      bValue = b.abnormalities.length;
    }

    if (order === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  return (
    <Card elevation={2}>
      <CardContent>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            Analysis Results Summary
          </Typography>
          {onExportData && (
            <Button
              variant="outlined"
              startIcon={<ExportIcon />}
              onClick={onExportData}
              size="small"
            >
              Export Data
            </Button>
          )}
        </Box>

        {/* Filters */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search by image name or abnormality..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 300 }}
          />
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={statusFilter}
              label="Status Filter"
              onChange={(e) => setStatusFilter(e.target.value as any)}
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="normal">Normal Only</MenuItem>
              <MenuItem value="abnormal">Abnormal Only</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Results Count */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Showing {sortedData.length} of {data.length} results
          {statusFilter !== 'all' && ` (filtered by ${statusFilter})`}
        </Typography>

        {/* Table */}
        <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Image</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'uploadTime'}
                    direction={orderBy === 'uploadTime' ? order : 'asc'}
                    onClick={() => handleRequestSort('uploadTime')}
                  >
                    Upload Time
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">
                  <TableSortLabel
                    active={orderBy === 'overallStatus'}
                    direction={orderBy === 'overallStatus' ? order : 'asc'}
                    onClick={() => handleRequestSort('overallStatus')}
                  >
                    Overall Status
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">L3</TableCell>
                <TableCell align="center">L4</TableCell>
                <TableCell align="center">L5</TableCell>
                <TableCell align="center">Sacrum</TableCell>
                <TableCell align="center">L3-L4 Spacing</TableCell>
                <TableCell align="center">L4-L5 Spacing</TableCell>
                <TableCell align="center">L5-Sacrum Spacing</TableCell>
                <TableCell align="center">
                  <TableSortLabel
                    active={orderBy === 'confidence'}
                    direction={orderBy === 'confidence' ? order : 'asc'}
                    onClick={() => handleRequestSort('confidence')}
                  >
                    Confidence
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">Abnormalities</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedData.map((row) => (
                <TableRow 
                  key={row.id} 
                  hover 
                  sx={{ 
                    '&:hover': { 
                      backgroundColor: 'action.hover',
                      cursor: 'pointer'
                    } 
                  }}
                  onClick={() => onViewDetails(row.id)}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar
                        variant="rounded"
                        sx={{ 
                          width: 40, 
                          height: 40, 
                          bgcolor: 'primary.light',
                          fontSize: '0.875rem'
                        }}
                      >
                        {row.imageName.substring(0, 2).toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {row.imageName.length > 20 
                            ? `${row.imageName.substring(0, 20)}...`
                            : row.imageName
                          }
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {new Date(row.uploadTime).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {getStatusChip(row.overallStatus)}
                  </TableCell>
                  <TableCell align="center">
                    {getStatusChip(row.l3Status)}
                  </TableCell>
                  <TableCell align="center">
                    {getStatusChip(row.l4Status)}
                  </TableCell>
                  <TableCell align="center">
                    {getStatusChip(row.l5Status)}
                  </TableCell>
                  <TableCell align="center">
                    {getStatusChip(row.sacrumStatus)}
                  </TableCell>
                  <TableCell align="center">
                    {getSpacingStatus(row.l3l4Spacing)}
                  </TableCell>
                  <TableCell align="center">
                    {getSpacingStatus(row.l4l5Spacing)}
                  </TableCell>
                  <TableCell align="center">
                    {getSpacingStatus(row.l5SacrumSpacing)}
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {Math.round(row.confidence * 100)}%
                      </Typography>
                      {row.confidence >= 0.8 ? (
                        <NormalIcon color="success" sx={{ fontSize: 16 }} />
                      ) : row.confidence >= 0.6 ? (
                        <WarningIcon color="warning" sx={{ fontSize: 16 }} />
                      ) : (
                        <AbnormalIcon color="error" sx={{ fontSize: 16 }} />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={row.abnormalities.length}
                      color={row.abnormalities.length === 0 ? 'success' : 'error'}
                      size="small"
                      sx={{ fontWeight: 500 }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Box onClick={(e) => e.stopPropagation()}>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => onViewDetails(row.id)}
                          color="primary"
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download Report">
                        <IconButton
                          size="small"
                          color="secondary"
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Empty State */}
        {sortedData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <FilterIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No results match your filters
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try adjusting your search terms or filter settings
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ResultsTable;