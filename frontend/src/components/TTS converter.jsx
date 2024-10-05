import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Volume2, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const API_URL = import.meta.env.VITE_API_URL || '';

// Expanded voice options
const voices = {
  english: {
    label: 'English Voices',
    options: {
      // United States
      'Emma (US)': 'en-US-EmmaNeural',
      'Jenny (US)': 'en-US-JennyNeural',
      'Guy (US)': 'en-US-GuyNeural',
      'Aria (US)': 'en-US-AriaNeural',
      'Davis (US)': 'en-US-DavisNeural',
      'Tony (US)': 'en-US-TonyNeural',
      'Sara (US)': 'en-US-SaraNeural',
      'Nancy (US)': 'en-US-NancyNeural',
      // United Kingdom
      'Jane (UK)': 'en-GB-SoniaNeural',
      'Ryan (UK)': 'en-GB-RyanNeural',
      'Libby (UK)': 'en-GB-LibbyNeural',
      'Oliver (UK)': 'en-GB-OliverNeural',
      // Australia
      'Natasha (AU)': 'en-AU-NatashaNeural',
      'William (AU)': 'en-AU-WilliamNeural',
      'Jenny (AU)': 'en-AU-JennyNeural',
      // Canada
      'Clara (CA)': 'en-CA-ClaraNeural',
      'Liam (CA)': 'en-CA-LiamNeural',
    }
  },
  indian: {
    label: 'Indian Languages',
    options: {
      // Hindi
      'Swara (HI)': 'hi-IN-SwaraNeural',
      'Madhur (HI)': 'hi-IN-MadhurNeural',
      // Tamil
      'Pallavi (TA)': 'ta-IN-PallaviNeural',
      'Valluvar (TA)': 'ta-IN-ValluvarNeural',
      // Telugu
      'Mohan (TE)': 'te-IN-MohanNeural',
      'Shruti (TE)': 'te-IN-ShrutiNeural',
      // Malayalam
      'Sobhana (ML)': 'ml-IN-SobhanaNeural',
      'Midhun (ML)': 'ml-IN-MidhunNeural',
      // Kannada
      'Gagan (KN)': 'kn-IN-GaganNeural',
      'Sapna (KN)': 'kn-IN-SapnaNeural',
      // Gujarati
      'Dhwani (GU)': 'gu-IN-DhwaniNeural',
      'Niranjan (GU)': 'gu-IN-NiranjanNeural',
      // Marathi
      'Aarohi (MR)': 'mr-IN-AarohiNeural',
      'Manohar (MR)': 'mr-IN-ManoharNeural',
      // Bengali
      'Tanishaa (BN)': 'bn-IN-TanishaaNeural',
      'Bashkar (BN)': 'bn-IN-BashkarNeural',
    }
  },
  european: {
    label: 'European Languages',
    options: {
      // French
      'Denise (FR)': 'fr-FR-DeniseNeural',
      'Henri (FR)': 'fr-FR-HenriNeural',
      // German
      'Katja (DE)': 'de-DE-KatjaNeural',
      'Conrad (DE)': 'de-DE-ConradNeural',
      // Spanish
      'Elvira (ES)': 'es-ES-ElviraNeural',
      'Alvaro (ES)': 'es-ES-AlvaroNeural',
      // Italian
      'Elsa (IT)': 'it-IT-ElsaNeural',
      'Diego (IT)': 'it-IT-DiegoNeural',
      // Portuguese
      'Fernanda (PT)': 'pt-PT-FernandaNeural',
      'Raul (PT)': 'pt-PT-RaulNeural',
    }
  },
  asian: {
    label: 'Asian Languages',
    options: {
      // Chinese (Mandarin)
      'Xiaoxiao (CN)': 'zh-CN-XiaoxiaoNeural',
      'Yunyang (CN)': 'zh-CN-YunyangNeural',
      // Japanese
      'Nanami (JP)': 'ja-JP-NanamiNeural',
      'Keita (JP)': 'ja-JP-KeitaNeural',
      // Korean
      'Sun-Hi (KR)': 'ko-KR-SunHiNeural',
      'In-Ho (KR)': 'ko-KR-InJoonNeural',
      // Vietnamese
      'Hoai My (VN)': 'vi-VN-HoaiMyNeural',
      'Nam Minh (VN)': 'vi-VN-NamMinhNeural',
    }
  },
  multi: {
    label: 'Multi-language Models',
    options: {
      'Emma (Multi)': 'en-US-EmmaMultilingualNeural',
      'Jenny (Multi)': 'en-US-JennyMultilingualNeural',
      'Ryan (Multi)': 'en-GB-RyanMultilingualNeural',
      'Aria (Multi)': 'en-US-AriaMultilingualNeural',
      'Guy (Multi)': 'fr-FR-VivienneMultilingualNeural',
      'Serafina (Multi)': 'de-DE-SeraphinaMultilingualNeural',
      'Florian (Multi)': 'de-DE-FlorianMultilingualNeural',
    }
  }
};

export default function TTSConverter() {
  const [text, setText] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('en-US-EmmaNeural');
  const [category, setCategory] = useState('english');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const audioRef = useRef(null);

  const handleCategoryChange = (newCategory) => {
    setCategory(newCategory);
    // Set first voice of the category as default
    const firstVoice = Object.values(voices[newCategory].options)[0];
    setSelectedVoice(firstVoice);
  };

  const handleVoiceChange = (voice) => {
    setSelectedVoice(voice);
  };

  const handleSubmit = async () => {
    if (!text.trim()) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/api/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          voice: selectedVoice,
        }),
      });
      
      if (!response.ok) {
        throw new Error('TTS conversion failed');
      }
      
      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
      }
    } catch (error) {
      setError('Failed to convert text to speech. Please try again.');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="w-full">
        <CardHeader>
          <h1 className="text-2xl font-bold text-center">Text to Speech Converter</h1>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Voice Category Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Language Category</label>
            <Select value={category} onValueChange={handleCategoryChange}>
              <SelectTrigger>
                <SelectValue>{voices[category].label}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {Object.keys(voices).map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {voices[cat].label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Voice Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Voice</label>
            <Select value={selectedVoice} onValueChange={handleVoiceChange}>
              <SelectTrigger>
                <SelectValue>
                  {Object.entries(voices[category].options).find(([_, value]) => value === selectedVoice)?.[0]}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {Object.entries(voices[category].options).map(([name, value]) => (
                  <SelectItem key={value} value={value}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Text Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Enter Text</label>
            <Textarea
              placeholder="Type or paste your text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="h-32"
            />
          </div>

          {/* Convert Button */}
          <Button
            onClick={handleSubmit}
            disabled={isLoading || !text.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Converting...
              </>
            ) : (
              <>
                <Volume2 className="mr-2 h-4 w-4" />
                Convert to Speech
              </>
            )}
          </Button>

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Hidden audio element for playback */}
          <audio ref={audioRef} className="hidden" controls />
        </CardContent>
      </Card>
    </div>
  );
}
