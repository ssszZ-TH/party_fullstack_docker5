import { Button } from '@mui/material';

interface ListSentButtonProps {
  onClick: () => void;
}

export default function ListSentButton({ onClick }: ListSentButtonProps) {
  return (
    <Button
      variant="contained"
      color="primary"
      onClick={onClick}
      sx={{ textTransform: 'none' }}
    >
      Sent
    </Button>
  );
}